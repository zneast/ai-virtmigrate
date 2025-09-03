# © 2025 AI-VirtMigrate. All rights reserved.

import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import json
import sys
import os
from rich.console import Console
from rich.table import Table
from rich.text import Text
import warnings
warnings.filterwarnings('ignore')  # Suppress sklearn warnings

# Initialize rich console
console = Console()

# Target platforms and their requirements
platforms = {
    'Proxmox VE': {
        'min_vCPUs': 1, 'min_RAM_GB': 2, 'min_Storage_GB': 10,
        'OS_Support': ['Ubuntu', 'Windows', 'CentOS', 'Rocky', 'AlmaLinux', 'Debian', 'Fedora', 'RHEL', 'openSUSE', 'Oracle'],
        'K8s_Compatible': False, 'Downtime_Factor': 1.0
    },
    'XCP-ng': {
        'min_vCPUs': 1, 'min_RAM_GB': 2, 'min_Storage_GB': 20,
        'OS_Support': ['Ubuntu', 'Windows', 'CentOS', 'Debian', 'RHEL'],
        'K8s_Compatible': False, 'Downtime_Factor': 1.1
    },
    'KVM': {
        'min_vCPUs': 1, 'min_RAM_GB': 1, 'min_Storage_GB': 10,
        'OS_Support': ['Ubuntu', 'Windows', 'CentOS', 'Rocky', 'AlmaLinux', 'Debian', 'Fedora', 'RHEL', 'openSUSE', 'Oracle'],
        'K8s_Compatible': True, 'Downtime_Factor': 0.9
    },
    'Harvester': {
        'min_vCPUs': 2, 'min_RAM_GB': 4, 'min_Storage_GB': 50,
        'OS_Support': ['Ubuntu', 'Windows', 'CentOS', 'Rocky', 'AlmaLinux', 'Debian', 'Fedora'],
        'K8s_Compatible': True, 'Downtime_Factor': 1.2
    },
    'Hyper-V': {
        'min_vCPUs': 1, 'min_RAM_GB': 1, 'min_Storage_GB': 10,
        'OS_Support': ['Ubuntu', 'Windows', 'CentOS', 'Rocky', 'AlmaLinux', 'Debian', 'Fedora', 'RHEL'],
        'K8s_Compatible': False, 'Downtime_Factor': 1.0, 'Note': 'Requires Windows Server license'
    },
    'OpenShift': {
        'min_vCPUs': 1, 'min_RAM_GB': 4, 'min_Storage_GB': 50,
        'OS_Support': ['Ubuntu', 'Windows', 'CentOS', 'Rocky', 'AlmaLinux', 'Debian', 'Fedora', 'RHEL', 'SUSE'],
        'K8s_Compatible': True, 'Downtime_Factor': 1.1, 'Note': 'Requires OpenShift cluster; certified for specific versions'
    },
    'Nutanix AHV': {
        'min_vCPUs': 1, 'min_RAM_GB': 1, 'min_Storage_GB': 10,
        'OS_Support': ['Ubuntu', 'Windows', 'CentOS', 'Rocky', 'AlmaLinux', 'Debian', 'Fedora', 'RHEL', 'Oracle'],
        'K8s_Compatible': False, 'Downtime_Factor': 1.0, 'Note': 'Requires Nutanix infrastructure (hardware or cloud)'
    }
}

# Expanded simulated historical migration data
migration_data = pd.DataFrame([
    {'vCPUs': 2, 'RAM_GB': 4, 'Storage_GB': 100, 'OS': 'Ubuntu', 'Target': 'Proxmox VE', 'Success': 1, 'Downtime_Hrs': 0.5},
    {'vCPUs': 4, 'RAM_GB': 8, 'Storage_GB': 200, 'OS': 'Windows', 'Target': 'XCP-ng', 'Success': 1, 'Downtime_Hrs': 1.0},
    {'vCPUs': 1, 'RAM_GB': 2, 'Storage_GB': 50, 'OS': 'Ubuntu', 'Target': 'KVM', 'Success': 1, 'Downtime_Hrs': 0.3},
    {'vCPUs': 8, 'RAM_GB': 16, 'Storage_GB': 500, 'OS': 'CentOS', 'Target': 'Harvester', 'Success': 0, 'Downtime_Hrs': 2.0},
    {'vCPUs': 12, 'RAM_GB': 12, 'Storage_GB': 300, 'OS': 'Windows', 'Target': 'KVM', 'Success': 1, 'Downtime_Hrs': 0.8},
    {'vCPUs': 16, 'RAM_GB': 32, 'Storage_GB': 1000, 'OS': 'Ubuntu', 'Target': 'Proxmox VE', 'Success': 1, 'Downtime_Hrs': 1.2},
    {'vCPUs': 14, 'RAM_GB': 14, 'Storage_GB': 100, 'OS': 'Rocky', 'Target': 'KVM', 'Success': 1, 'Downtime_Hrs': 1.5},
    {'vCPUs': 14, 'RAM_GB': 14, 'Storage_GB': 100, 'OS': 'Windows', 'Target': 'Hyper-V', 'Success': 1, 'Downtime_Hrs': 1.0},
    {'vCPUs': 14, 'RAM_GB': 14, 'Storage_GB': 100, 'OS': 'RHEL', 'Target': 'OpenShift', 'Success': 1, 'Downtime_Hrs': 1.2},
    {'vCPUs': 14, 'RAM_GB': 14, 'Storage_GB': 100, 'OS': 'Ubuntu', 'Target': 'Nutanix AHV', 'Success': 1, 'Downtime_Hrs': 1.0}
])

# Display help with supported options
def display_help():
    console.print("[bold cyan]AI-VirtMigrate Help: Supported Input Options[/bold cyan]")
    console.print("© 2025 AI-VirtMigrate. All rights reserved.")
    console.print("Free version limited to single VM assessments. Premium version (bulk processing, custom reports) available at [Gumroad link TBD].")
    console.print("Assess VMware ESXi VM migration to open-source or alternative hypervisors.")
    console.print("[bold red]Advisory:[/bold red] This is a planning tool. Always validate compatibility with your environment’s specific hardware, software, and licensing.")
    console.print("[bold]How Compatibility is Validated:[/bold] Compatibility is based on vendor documentation (e.g., Nutanix, Red Hat, Microsoft), community feedback (Reddit, X), and 2025 market reports. The tool checks VM specs (vCPUs, RAM, Storage, OS) against platform requirements. Success probability uses a decision tree trained on simulated data; downtime is estimated via heuristics. Verify edge cases (e.g., drivers, licensing) manually.")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Field", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Supported Values", style="green")
    table.add_column("Examples", style="yellow")
    
    supported_oses = sorted(set(os for platform in platforms.values() for os in platform['OS_Support']))
    table.add_row(
        "vCPUs", "Number of virtual CPUs", "Positive integers (1+)", "2, 4, 8, 14, 30"
    )
    table.add_row(
        "RAM (GB)", "Memory in gigabytes", "Positive integers (1+)", "4, 8, 14, 32, 64"
    )
    table.add_row(
        "Storage (GB)", "Disk storage in gigabytes", "Positive integers (1+)", "50, 100, 200, 500"
    )
    table.add_row(
        "OS", "Operating system (case-insensitive, partial match)", ", ".join(supported_oses), 
        "Ubuntu 20.04, Windows Server 2022, Rocky Linux 8, RHEL 9"
    )
    table.add_row(
        "Workload Type", "Workload type (informational)", "Any string", "Web Server, SQL, Testing"
    )
    table.add_row(
        "Network IO (Mbps)", "Network bandwidth in megabits/second", "Positive integers (1+)", "100, 500, 1000"
    )
    console.print(table)
    console.print("[bold]Platform Notes:[/bold]")
    for platform, reqs in platforms.items():
        note = reqs.get('Note', '')
        console.print(f"- {platform}: Supports {', '.join(reqs['OS_Support'])}{'; ' + note if note else ''}")

# AI Agent: Assess migration feasibility for a single VM
def assess_migration_single(vm_specs, platforms, migration_data):
    compatible_platforms = []
    os_input = vm_specs.get('OS', '').lower()
    supported_oses = set(os for platform in platforms.values() for os in platform['OS_Support'])
    
    os_base = None
    for os in supported_oses:
        if os.lower() in os_input:
            os_base = os
            break
    
    if not os_base:
        return {"VM_Name": vm_specs['vm_name'], "error": f"OS '{os_input}' not supported. Supported: {', '.join(sorted(supported_oses))}. Verify your environment."}
    
    for platform, reqs in platforms.items():
        if (vm_specs['vCPUs'] >= reqs['min_vCPUs'] and
            vm_specs['RAM_GB'] >= reqs['min_RAM_GB'] and
            vm_specs['Storage_GB'] >= reqs['min_Storage_GB'] and
            os_base in reqs['OS_Support']):
            compatible_platforms.append(platform)
    
    if not compatible_platforms:
        return {"VM_Name": vm_specs['vm_name'], "error": f"No compatible platforms for specs (OS: {os_base}). Verify your environment."}
    
    X = migration_data[['vCPUs', 'RAM_GB', 'Storage_GB']]
    y_success = migration_data['Success']
    y_downtime = migration_data['Downtime_Hrs']
    
    clf_success = DecisionTreeClassifier(random_state=42)
    clf_success.fit(X, y_success)
    
    input_data = pd.DataFrame([[vm_specs['vCPUs'], vm_specs['RAM_GB'], vm_specs['Storage_GB']]],
                              columns=['vCPUs', 'RAM_GB', 'Storage_GB'])
    downtime_estimates = {}
    for platform in compatible_platforms:
        success_prob = clf_success.predict_proba(input_data)[0][1]
        downtime = y_downtime.mean() * (vm_specs['vCPUs'] / X['vCPUs'].mean()) * platforms[platform]['Downtime_Factor']
        downtime_estimates[platform] = {
            'Success_Probability': round(success_prob, 2), 
            'Est_Downtime_Hrs': round(downtime, 2),
            'Note': platforms[platform].get('Note', '')
        }
    
    migration_plan = {
        'VM_Name': vm_specs['vm_name'],
        'Compatible_Platforms': compatible_platforms,
        'Risk_Assessment': downtime_estimates,
        'Sample_Migration_Script': '# Sample script (pseudocode)\n# Export VM from ESXi: esxcli vm process kill\n# Convert VMDK to QCOW2 (or VHDX for Hyper-V): qemu-img convert\n# Import to {platform}: virt-install (or New-VM for Hyper-V, oc create for OpenShift, nutanix-import for Nutanix AHV) ...'
    }
    
    # Placeholder for premium feature: custom report export
    # if premium_enabled:
    #     save_custom_report(migration_plan, format='csv')  # Example for CSV export
    
    return migration_plan

# Pretty print result using rich
def print_pretty_result(bulk_result, vm_specs_list):
    console.print("[bold red]Advisory:[/bold red] This is a planning tool. Always validate compatibility with your environment’s specific hardware, software, and licensing.")
    console.print("Free version limited to single VM assessments. Premium version (bulk processing, custom reports) available at [Gumroad link TBD].")
    for idx, result in enumerate(bulk_result):
        console.print(f"\n[bold cyan]Migration Plan for VM: {result['VM_Name']}[/bold cyan]")
        
        if "error" in result:
            console.print(f"[bold red]Error: {result['error']}[/bold red]")
            continue
        
        console.print(f"[bold]VM Specs[/bold]")
        specs = vm_specs_list[idx]
        console.print(f"  OS: {specs.get('OS', 'N/A')}")
        console.print(f"  vCPUs: {specs.get('vCPUs', 'N/A')}")
        console.print(f"  RAM: {specs.get('RAM_GB', 'N/A')} GB")
        console.print(f"  Storage: {specs.get('Storage_GB', 'N/A')} GB")
        console.print(f"  Workload: {specs.get('Workload_Type', 'N/A')}")
        
        console.print(f"[bold]Compatible Platforms[/bold]: {', '.join(result['Compatible_Platforms'])}")
        
        table = Table(title="Risk Assessment", show_header=True, header_style="bold magenta")
        table.add_column("Platform", style="cyan")
        table.add_column("Success Probability", justify="right", style="green")
        table.add_column("Est. Downtime (hrs)", justify="right", style="yellow")
        table.add_column("Notes", style="white")
        for platform, metrics in result['Risk_Assessment'].items():
            success_style = "green" if metrics['Success_Probability'] >= 0.7 else "red"
            table.add_row(platform, Text(str(metrics['Success_Probability']), style=success_style), 
                         str(metrics['Est_Downtime_Hrs']), metrics['Note'])
        console.print(table)
        
        console.print(f"[bold]Sample Migration Script[/bold]")
        console.print(result['Sample_Migration_Script'], style="dim")
    
    with open('migration_plan.json', 'w') as f:
        json.dump(bulk_result, f, indent=2)
    console.print(f"\n[bold green]JSON output saved to migration_plan.json[/bold green]")

# Bulk assessment function (disabled in freemium)
def assess_migration_bulk(vm_specs_list, platforms, migration_data):
    bulk_results = []
    for vm_specs in vm_specs_list:
        result = assess_migration_single(vm_specs, platforms, migration_data)
        bulk_results.append(result)
    return bulk_results

# Interactive prompt for single VM with validation
def prompt_single_vm():
    supported_oses = sorted(set(os for platform in platforms.values() for os in platform['OS_Support']))
    os_prompt = f"Enter OS (e.g., {', '.join(supported_oses)}): "
    vm_specs = {}
    try:
        vm_specs['vm_name'] = input("Enter VM name (e.g., TestVM1): ") or 'TestVM1'
        vm_specs['vCPUs'] = int(input("Enter vCPUs (positive integer, e.g., 2): ") or 2)
        if vm_specs['vCPUs'] <= 0:
            raise ValueError("vCPUs must be positive")
        vm_specs['RAM_GB'] = int(input("Enter RAM in GB (positive integer, e.g., 4): ") or 4)
        if vm_specs['RAM_GB'] <= 0:
            raise ValueError("RAM must be positive")
        vm_specs['Storage_GB'] = int(input("Enter Storage in GB (positive integer, e.g., 100): ") or 100)
        if vm_specs['Storage_GB'] <= 0:
            raise ValueError("Storage must be positive")
        vm_specs['OS'] = input(os_prompt) or 'Ubuntu 20.04'
        vm_specs['Workload_Type'] = input("Enter Workload Type (e.g., Web Server, SQL): ") or 'Web Server'
        vm_specs['Network_IO_Mbps'] = int(input("Enter Network IO in Mbps (positive integer, e.g., 100): ") or 100)
        if vm_specs['Network_IO_Mbps'] <= 0:
            raise ValueError("Network IO must be positive")
    except ValueError as e:
        console.print(f"[bold red]Error: {e}. Using default VM specs. Verify your environment.[/bold red]")
        return [{
            'vm_name': 'TestVM1', 'vCPUs': 2, 'RAM_GB': 4, 'Storage_GB': 100,
            'OS': 'Ubuntu 20.04', 'Workload_Type': 'Web Server', 'Network_IO_Mbps': 100
        }]
    return [vm_specs]

# Main execution (freemium: single VM only)
if __name__ == "__main__":
    console.print("[bold cyan]Welcome to AI-VirtMigrate! Run with --help for supported inputs.[/bold cyan]")
    console.print("© 2025 AI-VirtMigrate. All rights reserved.")
    console.print("[bold red]Advisory:[/bold red] This is a planning tool. Always validate compatibility with your environment’s specific hardware, software, and licensing.")
    console.print("Free version limited to single VM assessments. Premium version (bulk processing, custom reports) available at [Gumroad link TBD].")
    
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        display_help()
        sys.exit(0)
    
    # Freemium: Force single VM mode
    vm_specs_list = prompt_single_vm()
    
    bulk_result = assess_migration_bulk(vm_specs_list, platforms, migration_data)
    print_pretty_result(bulk_result, vm_specs_list)