from django.db import migrations


def reset_and_seed_checklist(apps, schema_editor):
    ChecklistItem = apps.get_model("orderform", "ChecklistItem")

    # Clear any old template rows (safe in dev – this is just the master checklist)
    ChecklistItem.objects.filter(drone_model="Bhumi A10E").delete()

    data = [
        # ===== STANDARD KIT =====
        # Description column: "Standard Kit"
        # Bhumi A10E Drone column:
        {"category": "STANDARD_KIT", "description": "Bhumi A10E Drone", "default_quantity": 1, "is_mandatory": True, "sort_order": 10},
        {"category": "STANDARD_KIT", "description": "Propeller Set (1 CW; 1 CCW)", "default_quantity": 3, "is_mandatory": True, "sort_order": 11},
        {"category": "STANDARD_KIT", "description": "Batteries Set (2 Nos.)", "default_quantity": 1, "is_mandatory": True, "sort_order": 12},
        {"category": "STANDARD_KIT", "description": "GPS System", "default_quantity": 1, "is_mandatory": True, "sort_order": 13},
        {"category": "STANDARD_KIT", "description": "Set complete accessories required for flight", "default_quantity": 1, "is_mandatory": True, "sort_order": 14},
        {"category": "STANDARD_KIT", "description": "Communication Air Module", "default_quantity": 1, "is_mandatory": True, "sort_order": 15},
        {"category": "STANDARD_KIT", "description": "Tool Kit", "default_quantity": 1, "is_mandatory": True, "sort_order": 16},
        {"category": "STANDARD_KIT", "description": "User Manual", "default_quantity": 1, "is_mandatory": True, "sort_order": 17},
        {"category": "STANDARD_KIT", "description": "Transportation Box", "default_quantity": 1, "is_mandatory": True, "sort_order": 18},

        # ===== PAYLOAD =====
        {"category": "PAYLOAD", "description": "10 Litre Pesticide tank", "default_quantity": 1, "is_mandatory": True, "sort_order": 20},
        {"category": "PAYLOAD", "description": "Camera for video feed", "default_quantity": 1, "is_mandatory": True, "sort_order": 21},

        # ===== GROUND CONTROL STATION =====
        {
            "category": "GCS",
            "description": "Ground Control Station with joystick, Integrated display",
            "default_quantity": 1,
            "is_mandatory": True,
            "sort_order": 30,
        },

        # ===== ACCESSORIES =====
        {"category": "ACCESSORIES", "description": "Nozzles", "default_quantity": 4, "is_mandatory": True, "sort_order": 40},
        {"category": "ACCESSORIES", "description": "Batteries Set (2 Nos.)", "default_quantity": 1, "is_mandatory": False, "sort_order": 41},

        # ===== SOFTWARE =====
        {
            "category": "SOFTWARE",
            "description": "Perpetual Ground Control Software for Mission Planning , Live Feed, And Data Status installed on GCS",
            "default_quantity": 1,
            "is_mandatory": True,
            "sort_order": 50,
        },

        # ===== FIELD TRAINING =====
        {
            "category": "FIELD_TRAINING",
            "description": "Hands on Training will be Provided at your Location",
            "default_quantity": 1,
            "is_mandatory": True,
            "sort_order": 60,
        },

        # ===== RPC PROGRAM =====
        {
            "category": "RPC_PROGRAM",
            "description": "Pilot training Program DGCA Certified",
            "default_quantity": 1,
            "is_mandatory": False,
            "sort_order": 61,
        },
    ]

    for item in data:
        ChecklistItem.objects.create(
            drone_model="Bhumi A10E",
            category=item["category"],
            description=item["description"],
            default_quantity=item["default_quantity"],
            is_mandatory=item["is_mandatory"],
            sort_order=item["sort_order"],
        )


def unreset_and_unseed(apps, schema_editor):
    ChecklistItem = apps.get_model("orderform", "ChecklistItem")
    ChecklistItem.objects.filter(drone_model="Bhumi A10E").delete()


class Migration(migrations.Migration):

    #  THIS IS THE FIX: 0002 depends on 0001_initial, not on itself
    dependencies = [
        ("orderform", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(reset_and_seed_checklist, unreset_and_unseed),
    ]
