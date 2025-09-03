# AI-VirtMigrate

© 2025 AI-VirtMigrate. All rights reserved.

## Overview
Tired of VMware's high costs post-Broadcom? AI-VirtMigrate is a free Python tool to plan ESXi VM migrations to alternatives like Proxmox VE, XCP-ng, KVM, Harvester, Hyper-V, OpenShift, and Nutanix AHV.

## Why It Exists
VMware's licensing hikes (150-1,200%) are pushing SMBs and home labs to open-source options. This tool streamlines planning, assessing compatibility and risks to save you time and avoid costly mistakes.

## How It Works
1. Install dependencies: `pip install pandas scikit-learn rich`.
2. Run `python migrate.py` (single mode: interactive prompts; bulk: JSON file).
3. Input VM specs (vCPUs, RAM, OS e.g., Rocky Linux).
4. Get output: Compatible platforms, risk table (success %, downtime), migration scripts.

Example output for a Rocky Linux VM:
[Insert screenshot or code block from your test]

Advisory: Planning tool only—validate your environment. Dynamic help: `python migrate.py --help`.

## Installation
Clone repo, run script. Free for basic use; premium features coming soon.

Contributions welcome, but respect copyright. Feedback? Open an issue!