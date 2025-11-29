from django.db import models


class Client(models.Model):
    """
    Client database table.

    client_id (PK), name, phone, email, location,
    id_proof, bank_name, account_number, ifsc_code, branch_name
    """

    client_id = models.CharField(
        max_length=20,
        primary_key=True,
        editable=False,
        unique=True,
    )

    name = models.CharField(max_length=255)

    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    # ID Proof (Aadhar, PAN, Passport, etc.)
    id_proof = models.CharField(max_length=255, blank=True, null=True)

    # Bank details
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    branch_name = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """
        Auto-generate client_id such as CLT_00001, CLT_00002, etc.
        """
        if not self.client_id:
            last = Client.objects.order_by("-client_id").first()
            if last:
                try:
                    last_num = int(last.client_id.split("_")[1])
                except Exception:
                    last_num = 0
            else:
                last_num = 0

            self.client_id = f"CLT_{last_num + 1:05d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client_id} - {self.name}"
