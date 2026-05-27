import csv
import os

csv_file_path = r"C:\lab-automation\employees.csv"
output_ps_path = r"C:\lab-automation\deploy_users.ps1"

# Baseline PowerShell configurations and active directory module ingestion
powershell_script = """# Active Directory Auto-Generated Deployment Script
Import-Module ActiveDirectory
"""

print("[*] Initializing Python Corporate Directory Parser...")

with open(csv_file_path, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    
    # Tracking array to ensure we don't write duplicate OU creation commands
    created_ous = set()
    
    for row in reader:
        first = row['Firstname'].strip()
        last = row['Lastname'].strip()
        dept = row['Department'].strip()
        title = row['JobTitle'].strip()
        
        # Structure enterprise layout strings
        sam_account_name = f"{first[0].lower()}{last.lower()}" # e.g., mvance
        user_principal_name = f"{sam_account_name}@enterprise.local"
        target_ou_path = f"OU={dept},OU=Staff,OU=Corp-Assets,DC=enterprise,DC=local"
        
        # Step 1: If the department OU doesn't exist in our tracking set, generate the AD command
        if dept not in created_ous:
            powershell_script += f'\n# Engineering OU Structure for {dept}\n'
            powershell_script += f'New-ADOrganizationalUnit -Name "{dept}" -Path "OU=Staff,OU=Corp-Assets,DC=enterprise,DC=local" -ProtectedFromAccidentalDeletion $true\n'
            created_ous.add(dept)
            
        # Step 2: Generate unique, complex temporary initialization passwords matching AD domain history rules
        temp_password = f"Init{first[:2].capitalize()}{last[:2].lower()}2026!"
        
        # Step 3: Build the structural Active Directory User Object creation block
        powershell_script += f'\n# Provisioning Account: {first} {last}\n'
        powershell_script += f'$Password = ConvertTo-SecureString "{temp_password}" -AsPlainText -Force\n'
        powershell_script += (
            f'New-ADUser -Name "{first} {last}" '
            f'-SamAccountName "{sam_account_name}" '
            f'-UserPrincipalName "{user_principal_name}" '
            f'-Title "{title}" '
            f'-Department "{dept}" '
            f'-Path "{target_ou_path}" '
            f'-AccountPassword $Password '
            f'-ChangePasswordAtLogon $true '
            f'-Enabled $true\n'
        )

# Flush the string buffer directly down to a native Windows PowerShell executable file
with open(output_ps_path, mode='w', encoding='utf-8') as ps_file:
    ps_file.write(powershell_script)

print(f"[+] Success! Enterprise deployment payload compiled flawlessly to: {output_ps_path}")
