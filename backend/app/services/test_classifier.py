from typing import TypedDict

from app.services.classifier import EmailClassifier


class TestEmail(TypedDict):
    name: str
    sender: str
    recipients: list[str]
    subject: str
    body: str


TEST_EMAILS: list[TestEmail] = [
    {
        "name": "BILL",
        "sender": "billing@netflix.com",
        "recipients": ["test.sample8400@gmail.com"],
        "subject": "Your Netflix payment is due",
        "body": """
Your Netflix subscription payment of $15.99 is due
on September 15, 2026.

Please ensure that your payment method is up to date.
""",
    },
    {
        "name": "MEETING",
        "sender": "hr@company.com",
        "recipients": ["test.sample8400@gmail.com"],
        "subject": "Interview scheduled for September 12",
        "body": """
We would like to schedule your technical interview
for September 12, 2026 at 3:00 PM.

Please confirm whether you are available.
""",
    },
    {
        "name": "FORM",
        "sender": "admissions@university.edu",
        "recipients": ["test.sample8400@gmail.com"],
        "subject": "Complete your application form",
        "body": """
Please complete the attached application form and
submit it before September 20, 2026.

Your application cannot be processed until the form
has been submitted.
""",
    },
    {
        "name": "REMINDER",
        "sender": "notifications@service.com",
        "recipients": ["test.sample8400@gmail.com"],
        "subject": "Reminder: document renewal",
        "body": """
This is a reminder that your account documents will
need to be renewed soon.

Please keep this in mind for your next renewal cycle.
""",
    },
    {
        "name": "SPAM",
        "sender": "offers@random-deals.com",
        "recipients": ["test.sample8400@gmail.com"],
        "subject": "Congratulations! You won a special offer!",
        "body": """
You have been selected for an exclusive limited-time
offer.

Click here to claim your amazing discount before it
expires!
""",
    },
    {
    "name": "OTHER",
    "sender": "notifications@github.com",
    "recipients": ["test.sample8400@gmail.com"],
    "subject": "Someone starred your repository",
    "body": """
Someone recently starred your GitHub repository.

Repository: InboxPilot

This is simply a notification about activity on your
repository. No action is required.
""",
},
]


def main():
    print("Testing InboxPilot classifier")
    print("=" * 60)

    classifier = EmailClassifier()

    passed = 0
    failed = 0

    for index, email in enumerate(TEST_EMAILS, start=1):
        print()
        print(f"--- Test {index}: {email['name']} ---")
        print(f"Subject: {email['subject']}")

        try:
            result = classifier.classify(
                sender=email["sender"],
                recipients=email["recipients"],
                subject=email["subject"],
                body=email["body"],
            )

            actual_category = result.category.value
            expected_category = email["name"]

            print(f"Expected:   {expected_category}")
            print(f"Actual:     {actual_category}")
            print(f"Confidence: {result.confidence}")
            print(f"Reasoning:  {result.reasoning}")

            if actual_category == expected_category:
                print("✅ PASS")
                passed += 1
            else:
                print("❌ FAIL")
                failed += 1

        except Exception as e:
            print("❌ ERROR")
            print(f"Error type: {type(e).__name__}")
            print(f"Error: {e}")
            failed += 1

    print()
    print("=" * 60)
    print("CLASSIFICATION TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {len(TEST_EMAILS)}")

    if failed == 0:
        print()
        print("✅ All classification tests passed!")
    else:
        print()
        print("⚠️ Some classification tests failed.")


if __name__ == "__main__":
    main()