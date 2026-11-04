import sys
import os
import time

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from colorama import init, Fore, Style
from src.orchestration.coordinator import A2ACoordinator
from src.protocol.messages import MessageType

init(autoreset=True)

DEMO_PROJECTS = [
    {
        "title": "Autonomous AI Healthcare Patient Portal",
        "desc": "Build a secure web and mobile patient portal featuring an AI diagnostic triage chatbot, HIPAA-compliant cloud infrastructure, and real-time medical data pipelines."
    },
    {
        "title": "Global Tech Leaders Annual Summit 2027",
        "desc": "Organize a 3-day corporate leadership conference in San Francisco including venue booking, marketing campaigns, sponsor contract negotiations, keynote PR, and VIP logistics."
    },
    {
        "title": "Fintech Mobile Banking App & Nationwide Launch",
        "desc": "Develop a React Native and Go-based banking app paired with regulatory GDPR/banking compliance audits, brand creative identity, and targeted social growth campaigns."
    },
    {
        "title": "Corporate Office Relocation & Culture Onboarding",
        "desc": "Manage the physical move of 500 employees to a new downtown facility, including vendor procurement, space planning, employee culture workshops, and financial budget tracking."
    }
]

def print_banner():
    print(Fore.CYAN + Style.BRIGHT + "=" * 76)
    print(Fore.CYAN + Style.BRIGHT + "   [A2A]  OFFICE PROJECT STAFFING: AGENT-TO-AGENT SYSTEM")
    print(Fore.CYAN + Style.BRIGHT + "   Agent 1: Project Strategist  <--->  Agent 2: Database Specialist")
    print(Fore.CYAN + Style.BRIGHT + "=" * 76 + Style.RESET_ALL)
    print()

def format_a2a_trace(message_dict):
    msg_type = message_dict.get("message_type")
    sender = message_dict.get("sender")
    recipient = message_dict.get("recipient")
    summary = message_dict.get("summary")
    reasoning = message_dict.get("reasoning")
    timestamp = message_dict.get("timestamp")

    if sender == "agent_project_planner":
        sender_badge = Fore.MAGENTA + Style.BRIGHT + "[AGENT 1: STRATEGIST]"
        arrow = Fore.WHITE + " -> "
        recip_badge = Fore.BLUE + f"[{recipient.upper()}]"
    elif sender == "agent_employee_db":
        sender_badge = Fore.BLUE + Style.BRIGHT + "[AGENT 2: DATABASE]"
        arrow = Fore.WHITE + " -> "
        recip_badge = Fore.MAGENTA + f"[{recipient.upper()}]"
    else:
        sender_badge = Fore.YELLOW + f"[{sender.upper()}]"
        arrow = " -> "
        recip_badge = Fore.WHITE + f"[{recipient.upper()}]"

    print(f"\n{sender_badge}{arrow}{recip_badge}  " + Fore.LIGHTBLACK_EX + f"({timestamp})")
    print(Fore.WHITE + Style.BRIGHT + f"  Type: {msg_type}")
    print(Fore.GREEN + f"  Summary: {summary}")
    if reasoning:
        print(Fore.LIGHTYELLOW_EX + f"  Reasoning: {reasoning}")

def print_final_roster(decision):
    print("\n" + Fore.GREEN + Style.BRIGHT + "=" * 76)
    print(Fore.GREEN + Style.BRIGHT + "                    FINAL ASSEMBLED TEAM ROSTER")
    print(Fore.GREEN + Style.BRIGHT + "=" * 76)

    category = decision.get("project_category", "").upper()
    team_size = decision.get("team_size", 0)
    metrics = decision.get("metrics", {})
    roster = decision.get("team_roster", [])

    print(Fore.CYAN + f"  Project Type:       {Fore.WHITE}{category}")
    print(Fore.CYAN + f"  Total Team Size:    {Fore.WHITE}{team_size} specialists")
    print(Fore.CYAN + f"  Avg Availability:   {Fore.WHITE}{metrics.get('average_availability_percent')}%")
    print(Fore.CYAN + f"  Avg Experience:     {Fore.WHITE}{metrics.get('average_experience_years')} years")
    print()

    print(Fore.YELLOW + Style.BRIGHT + f"{'ROLE':<30} {'EMPLOYEE':<18} {'DEPT':<18} {'MATCH':<8} {'AVAIL':<6}")
    print(Fore.LIGHTBLACK_EX + "-" * 82)
    for member in roster:
        role = member.get("assigned_role", "")[:28]
        name = member.get("employee_name", "")[:16]
        dept = member.get("department", "")[:16]
        match = f"{member.get('match_score', 0)}%"
        avail = f"{member.get('availability_percent', 0)}%"
        
        leadership_star = Fore.YELLOW + " *" if member.get("is_leadership") else "  "
        print(f"{Fore.WHITE}{role:<30}{leadership_star} {Fore.GREEN}{name:<18} {Fore.CYAN}{dept:<18} {Fore.MAGENTA}{match:<8} {Fore.WHITE}{avail:<6}")
        print(Fore.LIGHTBLACK_EX + f"    |-- Justification: {member.get('justification')}")
    print(Fore.GREEN + Style.BRIGHT + "=" * 76)

def main():
    print_banner()
    print("Choose an option:")
    for idx, d in enumerate(DEMO_PROJECTS, start=1):
        print(f"  [{idx}] Demo: {d['title']}")
    print("  [5] Custom Project (Type your own title & description)")
    print("  [0] Exit")
    print()

    try:
        choice = input(Fore.YELLOW + "Enter choice (1-5 or 0): " + Style.RESET_ALL).strip()
    except EOFError:
        choice = "1"

    if choice == "0":
        print("Goodbye!")
        sys.exit(0)

    if choice in ["1", "2", "3", "4"]:
        selected = DEMO_PROJECTS[int(choice) - 1]
        title = selected["title"]
        desc = selected["desc"]
    elif choice == "5":
        try:
            title = input(Fore.YELLOW + "Project Title: " + Style.RESET_ALL).strip()
            desc = input(Fore.YELLOW + "Project Description: " + Style.RESET_ALL).strip()
        except EOFError:
            title = "Internal Office Project"
            desc = "General cross-functional company initiative."
        if not title:
            title = "Internal Office Project"
        if not desc:
            desc = "General cross-functional company initiative."
    else:
        print(Fore.RED + "Invalid choice, defaulting to Demo 1.")
        title = DEMO_PROJECTS[0]["title"]
        desc = DEMO_PROJECTS[0]["desc"]

    print("\n" + Fore.CYAN + f"Starting A2A Collaboration for: '{title}'...")
    print(Fore.LIGHTBLACK_EX + f"Description: {desc}")

    coordinator = A2ACoordinator()

    # Stream messages in real-time as they are published to the bus
    def on_message_published(msg):
        format_a2a_trace(msg.model_dump())
        time.sleep(0.01)

    coordinator.bus.subscribe(on_message_published)

    result = coordinator.run_staffing_pipeline(title, desc)
    print_final_roster(result["decision"])

if __name__ == "__main__":
    main()
