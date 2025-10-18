# src/ghostai/proxy_api/firewall.py
# GhostAI Security Firewall - Advanced threat detection and blocking

from flask import Flask, request, jsonify
import requests, os, logging, yaml, time
from ghostai.pipeline.pipeline import Pipeline
from collections import defaultdict, deque
import hashlib
import json

class GhostAIFirewall:
    def __init__(self, api_base=None, api_key=None, config_path=None, use_mock=False, firewall_config=None):
        self.app = Flask(__name__)
        self.use_mock = use_mock
        self.mode = "firewall"
        
        # Load firewall configuration
        self.firewall_config = self._load_firewall_config(firewall_config)
        
        if use_mock:
            self.api_base = api_base or "http://localhost:5005"
            self.api_key = "mock-key"
        else:
            self.api_base = api_base or "https://api.openai.com/v1"
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        # resolve config file path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = config_path or os.path.join(base_dir, "config", "scanners.yaml")

        self.pipeline = Pipeline(config_path=config_path)
        
        # Rate limiting
        self.rate_limiter = defaultdict(lambda: deque())
        self.blocked_ips = set()
        self.blocked_requests = set()
        
        # Request cache
        self.request_cache = {}
        
        self._register_routes()
        
        logging.info(f"🔥 GhostAI Security Firewall initialized in {self.mode} mode")

    def _load_firewall_config(self, config_path=None):
        """Load firewall configuration from YAML file"""
        if config_path is None:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "firewall_config.yaml")
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config.get('firewall', {})
        except FileNotFoundError:
            logging.warning(f"Firewall config not found at {config_path}, using defaults")
            return self._get_default_config()
        except Exception as e:
            logging.error(f"Error loading firewall config: {e}, using defaults")
            return self._get_default_config()

    def _get_default_config(self):
        """Default firewall configuration"""
        return {
            'mode': 'firewall',
            'log_level': 'INFO',
            'max_request_size': 1048576,
            'timeout': 30,
            'policies': {
                'block_jailbreaks': True,
                'block_pii': True,
                'block_secrets': True,
                'block_malicious': True,
                'filter_responses': True,
                'sanitize_pii': True,
                'remove_secrets': True,
                'rate_limit': {'enabled': True, 'requests_per_minute': 1000, 'burst_size': 100},  # Increased for 1M/day
                'ip_blocking': {'enabled': False, 'blacklist': [], 'whitelist': []},
                'auth': {'enabled': False, 'api_key_required': False, 'jwt_required': False}
            },
            'thresholds': {
                'jailbreak_confidence': 0.7,  # Increased from 0.3 to reduce false positives
                'pii_confidence': 0.9,        # Increased from 0.8 to reduce false positives
                'secret_confidence': 0.95,    # Increased from 0.9 to reduce false positives
                'malicious_confidence': 0.8   # Increased from 0.7 to reduce false positives
            },
            'logging': {
                'enabled': True,
                'log_all_requests': True,
                'log_blocked_requests': True,
                'log_forwarded_requests': False,
                'retention_days': 30
            },
            'alerts': {
                'enabled': True,
                'email_notifications': False,
                'webhook_url': '',
                'alert_on_block': True,
                'alert_on_threat': True
            },
            'performance': {
                'max_concurrent_requests': 100,
                'cache_size': 1000,
                'cache_ttl': 300,
                'enable_compression': True
            }
        }

    def _check_rate_limit(self, ip_address):
        """Check if IP address is within rate limits"""
        if not self.firewall_config['policies']['rate_limit']['enabled']:
            return True
            
        now = time.time()
        minute_ago = now - 60
        
        # Clean old entries
        while self.rate_limiter[ip_address] and self.rate_limiter[ip_address][0] < minute_ago:
            self.rate_limiter[ip_address].popleft()
        
        # Check if within limits
        requests_per_minute = self.firewall_config['policies']['rate_limit']['requests_per_minute']
        if len(self.rate_limiter[ip_address]) >= requests_per_minute:
            return False
            
        # Add current request
        self.rate_limiter[ip_address].append(now)
        return True

    def _check_ip_blocking(self, ip_address):
        """Check if IP address is blocked"""
        ip_config = self.firewall_config['policies']['ip_blocking']
        if not ip_config['enabled']:
            return True
            
        # Check blacklist
        if ip_address in ip_config['blacklist']:
            return False
            
        # Check whitelist (if enabled)
        if ip_config['whitelist'] and ip_address not in ip_config['whitelist']:
            return False
            
        return True

    def _should_block_request(self, scan_result):
        """Determine if request should be blocked based on scan results"""
        policies = self.firewall_config['policies']
        thresholds = self.firewall_config['thresholds']
        
        # Handle both dict and object scan results
        if isinstance(scan_result, dict):
            breakdown = scan_result.get('breakdown', {})
        else:
            breakdown = getattr(scan_result, 'breakdown', {})
        
        # Check for jailbreaks
        if policies['block_jailbreaks']:
            for scanner_name, scanner_result in breakdown.items():
                if 'bert' in scanner_name.lower() and scanner_result.get('flagged', False):
                    confidence = scanner_result.get('score', 0)
                    if confidence >= thresholds['jailbreak_confidence']:
                        return True, f"Jailbreak detected (confidence: {confidence:.2f})"
        
        # Check for PII
        if policies['block_pii']:
            for scanner_name, scanner_result in breakdown.items():
                if 'presidio' in scanner_name.lower() and scanner_result.get('flagged', False):
                    confidence = scanner_result.get('score', 0)
                    if confidence >= thresholds['pii_confidence']:
                        return True, f"PII detected (confidence: {confidence:.2f})"
        
        # Check for secrets
        if policies['block_secrets']:
            for scanner_name, scanner_result in breakdown.items():
                if 'secret' in scanner_name.lower() and scanner_result.get('flagged', False):
                    confidence = scanner_result.get('score', 0)
                    if confidence >= thresholds['secret_confidence']:
                        return True, f"Secret detected (confidence: {confidence:.2f})"
        
        return False, None

    def _sanitize_response(self, response_text, scan_result):
        """Sanitize AI response based on scan results"""
        if not self.firewall_config['policies']['filter_responses']:
            return response_text
            
        sanitized = response_text
        
        # Remove PII from response
        if self.firewall_config['policies']['sanitize_pii']:
            if isinstance(scan_result, dict):
                breakdown = scan_result.get('breakdown', {})
                if isinstance(breakdown, dict):
                    for scanner_name, scanner_result in breakdown.items():
                        if 'presidio' in scanner_name.lower() and scanner_result.get('flagged', False):
                            # Simple PII replacement (in production, use more sophisticated methods)
                            sanitized = sanitized.replace("123-45-6789", "[SSN]")
                            sanitized = sanitized.replace("4111-1111-1111-1111", "[CREDIT_CARD]")
        
        # Remove secrets from response
        if self.firewall_config['policies']['remove_secrets']:
            if isinstance(scan_result, dict):
                breakdown = scan_result.get('breakdown', {})
                if isinstance(breakdown, dict):
                    for scanner_name, scanner_result in breakdown.items():
                        if 'secret' in scanner_name.lower() and scanner_result.get('flagged', False):
                            # Simple secret replacement
                            sanitized = sanitized.replace("secret123", "[SECRET]")
                            sanitized = sanitized.replace("password", "[PASSWORD]")
        
        return sanitized

    def _log_request(self, ip_address, user_agent, request_data, scan_result, action, reason=None):
        """Log request for security monitoring"""
        if not self.firewall_config['logging']['enabled']:
            return
            
        log_entry = {
            'timestamp': time.time(),
            'ip_address': ip_address,
            'user_agent': user_agent,
            'action': action,  # 'blocked', 'forwarded', 'filtered'
            'reason': reason,
            'scan_result': scan_result,
            'request_size': len(str(request_data))
        }
        
        if self.firewall_config['logging']['log_all_requests'] or \
           (action == 'blocked' and self.firewall_config['logging']['log_blocked_requests']) or \
           (action == 'forwarded' and self.firewall_config['logging']['log_forwarded_requests']):
            logging.info(f"🔥 FIREWALL {action.upper()}: {json.dumps(log_entry)}")

    def _register_routes(self):
        @self.app.route("/v1/chat/completions", methods=["POST"])
        def firewall_chat():
            try:
                # Extract request information
                ip_address = request.remote_addr
                user_agent = request.headers.get('User-Agent', 'unknown')
                session_id = request.headers.get('X-Session-ID', f'firewall-{int(time.time())}')
                
                # Check request size
                content_length = request.content_length or 0
                if content_length > self.firewall_config['max_request_size']:
                    return jsonify({
                        "error": "Request too large",
                        "code": "REQUEST_TOO_LARGE",
                        "max_size": self.firewall_config['max_request_size']
                    }), 413
                
                # Check IP blocking
                if not self._check_ip_blocking(ip_address):
                    self._log_request(ip_address, user_agent, {}, {}, 'blocked', 'IP blocked')
                    return jsonify({
                        "error": "Access denied",
                        "code": "IP_BLOCKED"
                    }), 403
                
                # Check rate limiting
                if not self._check_rate_limit(ip_address):
                    self._log_request(ip_address, user_agent, {}, {}, 'blocked', 'Rate limit exceeded')
                    return jsonify({
                        "error": "Rate limit exceeded",
                        "code": "RATE_LIMIT_EXCEEDED"
                    }), 429
                
                # Parse request body
                body = request.get_json()
                if not body:
                    return jsonify({"error": "No JSON body provided"}), 400
                
                # Check for duplicate requests (intelligent deduplication)
                # Only block exact duplicates from same IP within last 30 seconds
                request_content = ""
                if "messages" in body:
                    for msg in body["messages"]:
                        if msg.get("role") == "user":
                            request_content += msg.get("content", "")
                
                # Create hash based on content + IP + timestamp (rounded to 30-second intervals)
                current_time = time.time()
                time_window = int(current_time // 30) * 30  # 30-second windows
                duplicate_key = f"{ip_address}:{hashlib.md5(request_content.encode()).hexdigest()}:{time_window}"
                
                # Clean old entries (older than 1 minute)
                if hasattr(self, '_duplicate_timestamps'):
                    self._duplicate_timestamps = {k: v for k, v in self._duplicate_timestamps.items() 
                                                if current_time - v < 60}  # 1 minute
                else:
                    self._duplicate_timestamps = {}
                
                # Only block if same content from same IP in same 30-second window
                if duplicate_key in self._duplicate_timestamps:
                    return jsonify({
                        "error": "Duplicate request blocked",
                        "code": "DUPLICATE_REQUEST"
                    }), 400
                
                # Store current request key with timestamp
                self._duplicate_timestamps[duplicate_key] = current_time
                
                # 🔍 Run security scans
                scan_results = []
                if "messages" in body:
                    for msg in body["messages"]:
                        if msg.get("role") == "user":
                            text = msg["content"]
                            scan_result = self.pipeline.run(
                                text, 
                                session_id=session_id,
                                user_agent=user_agent,
                                ip_address=ip_address
                            )
                            scan_results.append(scan_result)
                            
                            # Check if request should be blocked
                            should_block, block_reason = self._should_block_request(scan_result)
                            if should_block:
                                self.blocked_requests.add(duplicate_key)
                                self._log_request(ip_address, user_agent, body, scan_result, 'blocked', block_reason)
                                return jsonify({
                                    "error": f"Request blocked: {block_reason}",
                                    "code": "SECURITY_VIOLATION",
                                    "scan_result": scan_result
                                }), 403
                            
                            # Apply text modifications (anonymization, etc.)
                            if isinstance(scan_result, dict):
                                breakdown = scan_result.get("breakdown", {})
                                if isinstance(breakdown, dict):
                                    for scanner_name, scanner_result in breakdown.items():
                                        extra = scanner_result.get("extra", {})
                                        if "anonymized" in extra:
                                            text = extra["anonymized"]
                                        elif "redacted" in extra:
                                            text = extra["redacted"]
                            
                            msg["content"] = text
                
                # 🚀 Forward to AI service
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
                
                if self.use_mock:
                    headers = {"Content-Type": "application/json"}
                
                resp = requests.post(
                    f"{self.api_base}/v1/chat/completions",
                    headers=headers,
                    json=body,
                    timeout=self.firewall_config['timeout'],
                )
                
                # Process response
                response_data = resp.json()
                
                # Sanitize response if needed
                if self.firewall_config['policies']['filter_responses'] and scan_results:
                    for choice in response_data.get('choices', []):
                        if 'message' in choice and 'content' in choice['message']:
                            original_content = choice['message']['content']
                            sanitized_content = self._sanitize_response(original_content, scan_results[0])
                            choice['message']['content'] = sanitized_content
                
                # Log successful request
                self._log_request(ip_address, user_agent, body, scan_results, 'forwarded')
                
                return jsonify(response_data), resp.status_code
                
            except Exception as e:
                logging.error(f"🔥 Firewall error: {str(e)}")
                return jsonify({
                    "error": f"Firewall error: {str(e)}",
                    "code": "FIREWALL_ERROR"
                }), 500

        @self.app.route("/health", methods=["GET"])
        def health_check():
            return jsonify({
                "service": "ghostai-firewall",
                "status": "healthy",
                "mode": self.mode,
                "timestamp": time.time()
            })

        @self.app.route("/firewall/stats", methods=["GET"])
        def firewall_stats():
            return jsonify({
                "blocked_requests": len(self.blocked_requests),
                "rate_limited_ips": len([ip for ip, times in self.rate_limiter.items() if len(times) > 0]),
                "blocked_ips": len(self.blocked_ips),
                "cache_size": len(self.request_cache)
            })

    def run(self, host="0.0.0.0", port=5004, debug=False):
        """Run the firewall server"""
        logging.info(f"🔥 Starting GhostAI Security Firewall on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    firewall = GhostAIFirewall(use_mock=True)
    firewall.run()
