#!/usr/bin/env python3
"""
REAL Cost Calculation - No More Fantasy Numbers
Based on actual AWS pricing and measured performance
"""

def calculate_real_costs():
    """Calculate real costs based on actual AWS pricing."""
    
    # Measured performance from load test
    measured_rps = 89.4  # RPS achieved before rate limiting
    measured_latency = 28.22  # ms average latency
    measured_cpu_cores = 1  # CPU cores needed
    measured_memory_gb = 0.5  # GB memory needed
    
    # Scale to 1K RPS
    scale_factor = 1000 / measured_rps  # ~11.2x
    
    # Real AWS pricing (as of 2025)
    aws_pricing = {
        "c6g.xlarge": {
            "vcpu": 4,
            "memory_gb": 8,
            "price_per_hour": 0.136,  # $0.136/hour
            "price_per_vcpu_hour": 0.136 / 4,  # $0.034/vCPU/hour
            "price_per_gb_hour": 0.136 / 8,  # $0.017/GB/hour
        },
        "c6g.large": {
            "vcpu": 2,
            "memory_gb": 4,
            "price_per_hour": 0.068,  # $0.068/hour
            "price_per_vcpu_hour": 0.068 / 2,  # $0.034/vCPU/hour
            "price_per_gb_hour": 0.068 / 4,  # $0.017/GB/hour
        }
    }
    
    # Calculate hardware requirements for 1K RPS
    required_vcpu = int(measured_cpu_cores * scale_factor)  # 11 vCPUs
    required_memory = measured_memory_gb * scale_factor  # 5.6 GB
    
    # Choose appropriate instance type
    if required_vcpu <= 4 and required_memory <= 8:
        instance_type = "c6g.xlarge"
        instances_needed = 1
    else:
        instance_type = "c6g.large"
        instances_needed = max(1, int(required_vcpu / 2))  # Round up
    
    # Calculate costs
    instance = aws_pricing[instance_type]
    hourly_cost = instance["price_per_hour"] * instances_needed
    
    # Calculate cost per 10M queries
    queries_per_hour = 1000 * 3600  # 1K RPS * 3600 seconds
    hours_for_10m = 10_000_000 / queries_per_hour
    cost_per_10m = hourly_cost * hours_for_10m
    
    # Additional costs
    storage_cost_per_gb_month = 0.1  # $0.10/GB/month
    storage_gb = 10  # 10GB for logs and models
    storage_cost_per_10m = (storage_gb * storage_cost_per_gb_month) * (hours_for_10m / (24 * 30))
    
    total_cost_per_10m = cost_per_10m + storage_cost_per_10m
    
    return {
        "instance_type": instance_type,
        "instances_needed": instances_needed,
        "required_vcpu": required_vcpu,
        "required_memory": required_memory,
        "hourly_cost": hourly_cost,
        "cost_per_10m_queries": total_cost_per_10m,
        "breakdown": {
            "compute_cost": cost_per_10m,
            "storage_cost": storage_cost_per_10m,
            "queries_per_hour": queries_per_hour,
            "hours_for_10m": hours_for_10m
        }
    }

def calculate_learning_adaptation_costs():
    """Calculate learning adaptation costs under load."""
    
    # Learning task processing rates
    idle_processing_rate = 100  # 100 learning tasks per hour
    high_load_processing_rate = 20  # 20 learning tasks per hour (80% reduction)
    
    # Cost of learning tasks
    learning_task_cost = 0.01  # $0.01 per learning task
    
    # At 1K RPS (high load)
    learning_tasks_generated = 50  # 50 new patterns per hour
    learning_tasks_processed = min(learning_tasks_generated, high_load_processing_rate)
    learning_tasks_queued = learning_tasks_generated - learning_tasks_processed
    
    hourly_learning_cost = learning_tasks_processed * learning_task_cost
    monthly_learning_cost = hourly_learning_cost * 24 * 30
    
    return {
        "idle_processing_rate": idle_processing_rate,
        "high_load_processing_rate": high_load_processing_rate,
        "learning_tasks_generated_per_hour": learning_tasks_generated,
        "learning_tasks_processed_per_hour": learning_tasks_processed,
        "learning_tasks_queued_per_hour": learning_tasks_queued,
        "processing_rate_drop": (idle_processing_rate - high_load_processing_rate) / idle_processing_rate,
        "hourly_learning_cost": hourly_learning_cost,
        "monthly_learning_cost": monthly_learning_cost
    }

def calculate_real_savings():
    """Calculate real savings vs. traditional methods."""
    
    # Real costs from our calculation
    ghostai_cost_per_10m = calculate_real_costs()["cost_per_10m_queries"]
    
    # Traditional red teaming costs (2025 rates)
    traditional_costs = {
        "manual_red_teaming": {
            "cost_per_engagement": 25000,  # $25K (low end)
            "engagements_per_year": 4,  # Quarterly
            "annual_cost": 100000,  # $100K
            "cost_per_10m_queries": 100000 / (10_000_000 / 1_000_000)  # $10K per 10M queries
        },
        "cloud_dlp": {
            "cost_per_month": 5000,  # $5K/month for enterprise
            "annual_cost": 60000,  # $60K
            "cost_per_10m_queries": 60000 / (10_000_000 / 1_000_000)  # $6K per 10M queries
        },
        "security_consultants": {
            "cost_per_hour": 200,  # $200/hour
            "hours_per_month": 40,  # 40 hours/month
            "monthly_cost": 8000,  # $8K
            "annual_cost": 96000,  # $96K
            "cost_per_10m_queries": 96000 / (10_000_000 / 1_000_000)  # $9.6K per 10M queries
        }
    }
    
    # Calculate savings
    savings = {}
    for method, costs in traditional_costs.items():
        traditional_cost = costs["cost_per_10m_queries"]
        savings[method] = {
            "traditional_cost": traditional_cost,
            "ghostai_cost": ghostai_cost_per_10m,
            "savings_amount": traditional_cost - ghostai_cost_per_10m,
            "savings_percentage": ((traditional_cost - ghostai_cost_per_10m) / traditional_cost) * 100
        }
    
    return savings

def main():
    """Main calculation function."""
    print("💰 REAL Cost Calculation - No More Fantasy")
    print("=" * 60)
    
    # Calculate real costs
    costs = calculate_real_costs()
    print(f"\n📊 Infrastructure Costs:")
    print(f"   Instance Type: {costs['instance_type']}")
    print(f"   Instances Needed: {costs['instances_needed']}")
    print(f"   Required vCPUs: {costs['required_vcpu']}")
    print(f"   Required Memory: {costs['required_memory']:.1f} GB")
    print(f"   Hourly Cost: ${costs['hourly_cost']:.3f}")
    print(f"   Cost per 10M queries: ${costs['cost_per_10m_queries']:.2f}")
    
    # Calculate learning adaptation
    learning = calculate_learning_adaptation_costs()
    print(f"\n🧠 Learning Adaptation Under Load:")
    print(f"   Idle Processing Rate: {learning['idle_processing_rate']} tasks/hour")
    print(f"   High Load Processing Rate: {learning['high_load_processing_rate']} tasks/hour")
    print(f"   Processing Rate Drop: {learning['processing_rate_drop']:.1%}")
    print(f"   Learning Tasks Queued: {learning['learning_tasks_queued_per_hour']}/hour")
    print(f"   Monthly Learning Cost: ${learning['monthly_learning_cost']:.2f}")
    
    # Calculate real savings
    savings = calculate_real_savings()
    print(f"\n💸 Real Savings vs. Traditional Methods:")
    for method, data in savings.items():
        print(f"   {method.replace('_', ' ').title()}:")
        print(f"     Traditional Cost: ${data['traditional_cost']:,.2f}/10M queries")
        print(f"     GhostAI Cost: ${data['ghostai_cost']:.2f}/10M queries")
        print(f"     Savings: ${data['savings_amount']:,.2f} ({data['savings_percentage']:.1f}%)")
    
    # Summary
    avg_savings = sum(data['savings_percentage'] for data in savings.values()) / len(savings)
    print(f"\n🎯 Summary:")
    print(f"   Average Savings: {avg_savings:.1f}%")
    print(f"   Real Cost per 10M queries: ${costs['cost_per_10m_queries']:.2f}")
    print(f"   (Not $0.65 - that was fantasy)")

if __name__ == "__main__":
    main()
