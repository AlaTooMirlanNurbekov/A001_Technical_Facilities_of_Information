# Simple Role-Based Access Control (RBAC) demo 
#
# Idea:
#   - We have roles: admin, manager, cashier, guest
#   - Each role has a set of permissions
#   - A user acts as one role and tries different actions

from typing import Dict, List

#define a small set of permissions for our demo system
PERMISSIONS = {
    "view_inventory",
    "edit_inventory",
    "process_sales",
    "view_reports",
    "manage_users",
    "configure_system",
}

#map each role to the permissions it has
ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "admin": [
        "view_inventory",
        "edit_inventory",
        "process_sales",
        "view_reports",
        "manage_users",
        "configure_system",
    ],
    "manager": [
        "view_inventory",
        "edit_inventory",
        "process_sales",
        "view_reports",
    ],
    "cashier": [
        "view_inventory",
        "process_sales",
    ],
    "guest": [
        "view_inventory",
    ],
}

def show_roles() -> None:
    """Print available roles and their permissions."""
    print("Available roles:\n")
    for role, perms in ROLE_PERMISSIONS.items():
        print(f"  {role}:")
        for p in perms:
            print(f"    - {p}")
        print()

def check_permission(role: str, permission: str) -> bool:
    """Return True if this role has the given permission."""
    perms = ROLE_PERMISSIONS.get(role)
    if perms is None:
        return False
    return permission in perms

def pick_role() -> str:
    """Ask the user to choose a role."""
    while True:
        role = input("Enter role (admin/manager/cashier/guest): ").strip().lower()
        if role in ROLE_PERMISSIONS:
            return role
        print("[!] Unknown role. Please choose one of: admin, manager, cashier, guest.")

def pick_permission() -> str:
    """Ask the user to choose an action (permission)."""
    print("\nActions you can try:")
    for p in sorted(PERMISSIONS):
        print(f"  - {p}")
    print()
    while True:
        perm = input("Type action name (or 'back' to choose role again): ").strip()
        if perm.lower() == "back":
            return "back"
        if perm in PERMISSIONS:
            return perm
        print("[!] Unknown action. Please type one of the listed permissions or 'back'.")

def main() -> None:
    print("=== TFI02 – Role-Based Access Control Demo ===\n")
    print("This small script shows how roles map to permissions.\n")
    show_roles()
    while True:
        print("-----------------------------------------")
        role = pick_role()
        print(f"\nYou are now acting as role: '{role}'")

        while True:
            perm = pick_permission()
            if perm == "back":
                # go back to role selection
                break
            if check_permission(role, perm):
                print(f"[ALLOW] Role '{role}' can perform action '{perm}'.")
            else:
                print(f"[DENY]  Role '{role}' is NOT allowed to perform '{perm}'.")
        #ask if user wants to quit completely
        again = input("\nDo you want to test another role? (y/n): ").strip().lower()
        if again != "y":
            print("Goodbye.")
            break

if __name__ == "__main__":
    main()
