"""
Tests for the institutional registration feature of the `pd` app.

Run with:  python manage.py test pd

What is covered (all based on the real models.py / forms.py / views.py / urls.py):
    A. InstitutionalTeam model  (fields, validators, clean() rules, __str__)
    B. InstitutionalTeamForm    (valid data, missing/invalid fields, cross-field rules)
    C. register_institutional view (GET, POST, messages, redirect)
    D. Email behaviour (the view does NOT call send_mail(), so we test that)
"""

from django.contrib.messages import get_messages
from django.core import mail
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .forms import InstitutionalTeamForm
from .models import InstitutionalTeam


# ---------------------------------------------------------------------------
# Helpers: one place that defines "good" data, so each test only changes
# the one thing it wants to check.
# ---------------------------------------------------------------------------

def valid_data(**overrides):
    """Return a dict of valid form data. Pass keyword args to override fields."""
    data = {
        "institution_name": "IIT Guwahati",
        "team_slots": 2,
        "adjudicator_slots": 1,
        "team_rep_names": "Rajnish Kumar",
        "contact_number": "9876543210",
        "email": "debate@example.com",
        # optional fields
        "alt_contact_name": "Priya Sharma",
        "alt_contact_email": "priya@example.com",
        "alt_contact_number": "8123456789",
    }
    data.update(overrides)
    return data


def make_team(**overrides):
    """Build (but do NOT save) an InstitutionalTeam with valid values."""
    return InstitutionalTeam(**valid_data(**overrides))


# ---------------------------------------------------------------------------
# A. MODEL TESTS
# ---------------------------------------------------------------------------

class InstitutionalTeamModelTests(TestCase):

    def test_create_and_save_team(self):
        """A valid team can be saved and read back from the database."""
        team = make_team()
        team.full_clean()  # runs field validators + clean()
        team.save()
        self.assertEqual(InstitutionalTeam.objects.count(), 1)
        saved = InstitutionalTeam.objects.get()
        self.assertEqual(saved.institution_name, "IIT Guwahati")
        self.assertEqual(saved.team_slots, 2)
        self.assertEqual(saved.adjudicator_slots, 1)

    def test_str_returns_institution_name(self):
        """__str__ should return the institution name."""
        self.assertEqual(str(make_team(institution_name="NIT Silchar")), "NIT Silchar")

    def test_created_at_is_set_automatically(self):
        """created_at is auto_now_add, so it is filled on save."""
        team = make_team()
        team.save()
        self.assertIsNotNone(team.created_at)

    def test_optional_fields_can_be_blank(self):
        """The three alternate-contact fields are optional."""
        team = make_team(alt_contact_name="", alt_contact_email="", alt_contact_number="")
        team.full_clean()  # should not raise

    def test_required_text_fields_cannot_be_blank(self):
        """Mandatory text fields raise a ValidationError when empty."""
        for field in ["institution_name", "team_rep_names", "contact_number", "email"]:
            with self.subTest(field=field):
                team = make_team(**{field: ""})
                with self.assertRaises(ValidationError) as ctx:
                    team.full_clean()
                self.assertIn(field, ctx.exception.message_dict)

    def test_slot_fields_cannot_be_null(self):
        """Both slot counts are required (no null, no default)."""
        for field in ["team_slots", "adjudicator_slots"]:
            with self.subTest(field=field):
                team = make_team(**{field: None})
                with self.assertRaises(ValidationError) as ctx:
                    team.full_clean()
                self.assertIn(field, ctx.exception.message_dict)

    def test_valid_phone_numbers_pass(self):
        """10 digits starting with 6, 7, 8 or 9 are accepted, with or without +91 prefix."""
        for number in ["6000000000", "7123456789", "8123456789", "9876543210", "+919876543210", "+91 9876543210", "+91-9876543210"]:
            with self.subTest(number=number):
                make_team(contact_number=number, alt_contact_number="").full_clean()

    def test_invalid_phone_numbers_fail(self):
        """Bad numbers are rejected: wrong start digit, too short/long, letters."""
        bad_numbers = [
            "5876543210",   # starts with 5
            "0123456789",   # starts with 0
            "987654321",    # 9 digits
            "98765432101",  # 11 digits without prefix
            "98765abcde",   # letters
            "9876 54321",   # contains an internal space
        ]
        for number in bad_numbers:
            with self.subTest(number=number):
                with self.assertRaises(ValidationError) as ctx:
                    make_team(contact_number=number).full_clean()
                self.assertIn("contact_number", ctx.exception.message_dict)

    def test_invalid_alt_phone_number_fails(self):
        """The same phone rule applies to the optional alternate number."""
        with self.assertRaises(ValidationError) as ctx:
            make_team(alt_contact_number="1234567890").full_clean()
        self.assertIn("alt_contact_number", ctx.exception.message_dict)

    def test_invalid_email_uses_custom_message(self):
        """A bad email gives the custom message defined on the model field."""
        with self.assertRaises(ValidationError) as ctx:
            make_team(email="not-an-email").full_clean()
        self.assertIn(
            "Please enter a valid email address, like ranjo@example.com.",
            ctx.exception.message_dict["email"],
        )

    def test_invalid_alt_email_uses_custom_message(self):
        with self.assertRaises(ValidationError) as ctx:
            make_team(alt_contact_email="bad@@mail").full_clean()
        self.assertIn(
            "Please enter a valid email address, like ranjo@example.com.",
            ctx.exception.message_dict["alt_contact_email"],
        )

    # ---- the rules inside InstitutionalTeam.clean() ----

    def test_clean_rejects_zero_team_and_zero_adjudicator_slots(self):
        """Requesting 0 team slots AND 0 adjudicator slots is not allowed."""
        with self.assertRaises(ValidationError) as ctx:
            make_team(team_slots=0, adjudicator_slots=0).full_clean()
        self.assertIn(
            "At least one team or adjudicator slot must be requested.",
            ctx.exception.message_dict["team_slots"],
        )

    def test_clean_allows_zero_for_only_one_slot_type(self):
        """Zero is fine as long as the other slot type is above zero."""
        make_team(team_slots=0, adjudicator_slots=3).full_clean()
        make_team(team_slots=3, adjudicator_slots=0).full_clean()

    def test_clean_rejects_alt_name_same_as_rep_name(self):
        with self.assertRaises(ValidationError) as ctx:
            make_team(team_rep_names="Rajnish Kumar", alt_contact_name="rajnish kumar").full_clean()
        self.assertIn(
            "Alternate point of contact name must be different from team representative name.",
            ctx.exception.message_dict["alt_contact_name"],
        )

    def test_clean_rejects_alt_email_same_as_main_email(self):
        with self.assertRaises(ValidationError) as ctx:
            make_team(email="a@example.com", alt_contact_email="a@example.com").full_clean()
        self.assertIn(
            "Alternate email must be different from the main email.",
            ctx.exception.message_dict["alt_contact_email"],
        )

    def test_clean_alt_email_comparison_ignores_case(self):
        """A@Example.com and a@example.com count as the same email."""
        with self.assertRaises(ValidationError) as ctx:
            make_team(email="a@example.com", alt_contact_email="A@Example.COM").full_clean()
        self.assertIn("alt_contact_email", ctx.exception.message_dict)

    def test_clean_rejects_alt_number_same_as_main_number(self):
        with self.assertRaises(ValidationError) as ctx:
            make_team(contact_number="9876543210", alt_contact_number="+919876543210").full_clean()
        self.assertIn(
            "Alternate number must be different from the main contact number.",
            ctx.exception.message_dict["alt_contact_number"],
        )

    def test_clean_collects_multiple_errors_together(self):
        """All clean() problems are reported at once, not one by one."""
        team = make_team(
            team_slots=0,
            adjudicator_slots=0,
            alt_contact_email="debate@example.com",   # same as main
            alt_contact_number="9876543210",          # same as main
        )
        with self.assertRaises(ValidationError) as ctx:
            team.full_clean()
        errors = ctx.exception.message_dict
        self.assertIn("team_slots", errors)
        self.assertIn("alt_contact_email", errors)
        self.assertIn("alt_contact_number", errors)

    def test_duplicate_institutions_are_not_allowed(self):
        """There is a unique constraint: the same institution cannot register twice."""
        team1 = make_team()
        team1.save()
        team2 = make_team()
        with self.assertRaises(ValidationError):
            team2.validate_unique()


# ---------------------------------------------------------------------------
# B. FORM TESTS
# ---------------------------------------------------------------------------

class InstitutionalTeamFormTests(TestCase):

    def test_form_contains_exactly_the_expected_fields(self):
        """The form exposes the nine fields in the documented order."""
        self.assertEqual(
            list(InstitutionalTeamForm().fields),
            [
                "institution_name", "team_slots", "adjudicator_slots",
                "team_rep_names", "contact_number", "email",
                "alt_contact_name", "alt_contact_email", "alt_contact_number",
            ],
        )

    def test_valid_data_is_accepted(self):
        form = InstitutionalTeamForm(data=valid_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_valid_form_saves_a_row(self):
        form = InstitutionalTeamForm(data=valid_data())
        self.assertTrue(form.is_valid(), form.errors)
        team = form.save()
        self.assertEqual(InstitutionalTeam.objects.count(), 1)
        self.assertEqual(team.email, "debate@example.com")

    def test_optional_fields_may_be_omitted(self):
        data = valid_data()
        for key in ["alt_contact_name", "alt_contact_email", "alt_contact_number"]:
            data.pop(key)
        form = InstitutionalTeamForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_each_required_field_is_enforced(self):
        """Leaving out any mandatory field makes the form invalid."""
        required = [
            "institution_name", "team_slots", "adjudicator_slots",
            "team_rep_names", "contact_number", "email",
        ]
        for field in required:
            with self.subTest(field=field):
                data = valid_data()
                data.pop(field)
                form = InstitutionalTeamForm(data=data)
                self.assertFalse(form.is_valid())
                self.assertIn(field, form.errors)

    def test_whitespace_only_institution_name_is_rejected(self):
        """Django strips spaces from text fields, so '   ' counts as empty."""
        form = InstitutionalTeamForm(data=valid_data(institution_name="   "))
        self.assertFalse(form.is_valid())
        self.assertIn("institution_name", form.errors)

    def test_surrounding_spaces_are_stripped_from_phone(self):
        """' 9876543210 ' is cleaned to '9876543210' before validation."""
        form = InstitutionalTeamForm(data=valid_data(contact_number=" 9876543210 "))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["contact_number"], "9876543210")

    def test_invalid_main_email_is_rejected(self):
        for bad in ["plainaddress", "missing@domain", "@no-user.com", "two@@example.com"]:
            with self.subTest(email=bad):
                form = InstitutionalTeamForm(data=valid_data(email=bad))
                self.assertFalse(form.is_valid())
                self.assertIn("email", form.errors)

    def test_invalid_alt_email_is_rejected(self):
        form = InstitutionalTeamForm(data=valid_data(alt_contact_email="nope"))
        self.assertFalse(form.is_valid())
        self.assertIn("alt_contact_email", form.errors)

    def test_invalid_phone_numbers_are_rejected(self):
        for bad in ["5876543210", "987654321", "98765432101", "98765abcde"]:
            with self.subTest(number=bad):
                form = InstitutionalTeamForm(data=valid_data(contact_number=bad))
                self.assertFalse(form.is_valid())
                self.assertIn("contact_number", form.errors)

    def test_invalid_alt_phone_number_is_rejected(self):
        form = InstitutionalTeamForm(data=valid_data(alt_contact_number="4123456789"))
        self.assertFalse(form.is_valid())
        self.assertIn("alt_contact_number", form.errors)

    def test_phone_validator_message_is_shown(self):
        form = InstitutionalTeamForm(data=valid_data(contact_number="5876543210"))
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Enter a valid 10-digit indian phone number(starting with digit 6-9).",
            form.errors["contact_number"],
        )

    def test_negative_slot_counts_are_rejected(self):
        for field in ["team_slots", "adjudicator_slots"]:
            with self.subTest(field=field):
                form = InstitutionalTeamForm(data=valid_data(**{field: -1}))
                self.assertFalse(form.is_valid())
                self.assertIn(field, form.errors)

    def test_non_numeric_slot_counts_are_rejected(self):
        for field in ["team_slots", "adjudicator_slots"]:
            with self.subTest(field=field):
                form = InstitutionalTeamForm(data=valid_data(**{field: "abc"}))
                self.assertFalse(form.is_valid())
                self.assertIn(field, form.errors)

    def test_decimal_slot_counts_are_rejected(self):
        form = InstitutionalTeamForm(data=valid_data(team_slots="1.5"))
        self.assertFalse(form.is_valid())
        self.assertIn("team_slots", form.errors)

    def test_zero_slots_boundary(self):
        """0 + 0 is invalid, but 0 + 1 and 1 + 0 are valid."""
        both_zero = InstitutionalTeamForm(data=valid_data(team_slots=0, adjudicator_slots=0))
        self.assertFalse(both_zero.is_valid())
        self.assertIn("team_slots", both_zero.errors)

        self.assertTrue(
            InstitutionalTeamForm(data=valid_data(team_slots=0, adjudicator_slots=1)).is_valid()
        )
        self.assertTrue(
            InstitutionalTeamForm(data=valid_data(team_slots=1, adjudicator_slots=0)).is_valid()
        )

    def test_alt_email_must_differ_from_main_email(self):
        form = InstitutionalTeamForm(
            data=valid_data(email="same@example.com", alt_contact_email="SAME@example.com")
        )
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Alternate email must be different from the main email.",
            form.errors["alt_contact_email"],
        )

    def test_alt_number_must_differ_from_main_number(self):
        form = InstitutionalTeamForm(
            data=valid_data(contact_number="9876543210", alt_contact_number="+919876543210")
        )
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Alternate number must be different from the main contact number.",
            form.errors["alt_contact_number"],
        )

    def test_overlong_institution_name_is_rejected(self):
        """institution_name has max_length=200."""
        form = InstitutionalTeamForm(data=valid_data(institution_name="A" * 201))
        self.assertFalse(form.is_valid())
        self.assertIn("institution_name", form.errors)
        self.assertTrue(
            InstitutionalTeamForm(data=valid_data(institution_name="A" * 200)).is_valid()
        )

    def test_overlong_team_rep_names_is_rejected(self):
        """team_rep_names has max_length=300."""
        form = InstitutionalTeamForm(data=valid_data(team_rep_names="B" * 301))
        self.assertFalse(form.is_valid())
        self.assertIn("team_rep_names", form.errors)


# ---------------------------------------------------------------------------
# C. VIEW TESTS
# ---------------------------------------------------------------------------

class RegisterInstitutionalViewTests(TestCase):

    def setUp(self):
        # reverse() looks the URL up by its name in pd/urls.py
        self.url = reverse("register_institutional")

    # ---- GET ----

    def test_get_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "register_institutional.html")

    def test_get_context_contains_unbound_form(self):
        response = self.client.get(self.url)
        self.assertIsInstance(response.context["form"], InstitutionalTeamForm)
        self.assertFalse(response.context["form"].is_bound)

    def test_get_does_not_create_anything(self):
        self.client.get(self.url)
        self.assertEqual(InstitutionalTeam.objects.count(), 0)

    def test_get_has_no_messages(self):
        response = self.client.get(self.url)
        self.assertEqual(list(get_messages(response.wsgi_request)), [])

    # ---- valid POST ----

    def test_valid_post_saves_registration(self):
        self.client.post(self.url, valid_data())
        self.assertEqual(InstitutionalTeam.objects.count(), 1)
        team = InstitutionalTeam.objects.get()
        self.assertEqual(team.institution_name, "IIT Guwahati")
        self.assertEqual(team.contact_number, "9876543210")
        self.assertEqual(team.email, "debate@example.com")
        self.assertEqual(team.alt_contact_name, "Priya Sharma")

    def test_valid_post_redirects_to_home(self):
        response = self.client.post(self.url, valid_data())
        self.assertRedirects(response, reverse("home"), fetch_redirect_response=False)

    def test_valid_post_adds_success_message(self):
        response = self.client.post(self.url, valid_data())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Registration submitted successfully!")
        self.assertEqual(messages[0].tags, "success")

    def test_valid_post_without_optional_fields_saves(self):
        data = valid_data(alt_contact_name="", alt_contact_email="", alt_contact_number="")
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse("home"), fetch_redirect_response=False)
        team = InstitutionalTeam.objects.get()
        self.assertEqual(team.alt_contact_email, "")

    def test_duplicate_institution_registration_is_rejected(self):
        """A repeated submission with the same institution name is rejected."""
        self.client.post(self.url, valid_data())
        self.assertEqual(InstitutionalTeam.objects.count(), 1)
        response = self.client.post(self.url, valid_data())
        self.assertEqual(InstitutionalTeam.objects.count(), 1)
        self.assertEqual(response.status_code, 200)
        self.assertIn("institution_name", response.context["form"].errors)

    # ---- invalid POST ----

    def test_invalid_post_does_not_save(self):
        self.client.post(self.url, valid_data(email="not-an-email"))
        self.assertEqual(InstitutionalTeam.objects.count(), 0)

    def test_invalid_post_rerenders_form_with_status_200(self):
        response = self.client.post(self.url, valid_data(email="not-an-email"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register_institutional.html")

    def test_invalid_post_returns_bound_form_with_errors(self):
        response = self.client.post(self.url, valid_data(email="not-an-email"))
        form = response.context["form"]
        self.assertTrue(form.is_bound)
        self.assertIn("email", form.errors)

    def test_invalid_post_adds_error_message(self):
        response = self.client.post(self.url, valid_data(email="not-an-email"))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Please correct the errors below.")
        self.assertEqual(messages[0].tags, "error")

    def test_invalid_post_does_not_redirect(self):
        response = self.client.post(self.url, valid_data(email="not-an-email"))
        self.assertNotIn(response.status_code, (301, 302))

    def test_invalid_post_keeps_submitted_values_in_page(self):
        """Typed values should come back so the user doesn't retype everything."""
        response = self.client.post(
            self.url, valid_data(institution_name="Keep Me College", email="bad")
        )
        self.assertContains(response, "Keep Me College")

    def test_invalid_post_shows_error_text_on_page(self):
        """The error message and the model's rule text appear in the HTML."""
        response = self.client.post(self.url, valid_data(team_slots=0, adjudicator_slots=0))
        self.assertContains(response, "Please correct the errors below.")
        self.assertContains(response, "At least one team or adjudicator slot must be requested.")

    def test_empty_post_reports_every_required_field(self):
        response = self.client.post(self.url, {})
        self.assertEqual(InstitutionalTeam.objects.count(), 0)
        errors = response.context["form"].errors
        for field in ["institution_name", "team_slots", "adjudicator_slots",
                      "team_rep_names", "contact_number", "email"]:
            with self.subTest(field=field):
                self.assertIn(field, errors)
        # optional fields must NOT be flagged
        for field in ["alt_contact_name", "alt_contact_email", "alt_contact_number"]:
            with self.subTest(field=field):
                self.assertNotIn(field, errors)

    def test_cross_field_rules_block_saving(self):
        """The model's clean() rules also stop a save through the view."""
        bad_posts = {
            "alt email same as main": valid_data(alt_contact_email="debate@example.com"),
            "alt number same as main": valid_data(alt_contact_number="9876543210"),
            "zero slots": valid_data(team_slots=0, adjudicator_slots=0),
        }
        for label, data in bad_posts.items():
            with self.subTest(case=label):
                response = self.client.post(self.url, data)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(InstitutionalTeam.objects.count(), 0)


class HomeViewTests(TestCase):
    """The success redirect lands on 'home', so make sure that page works."""

    def test_home_page_loads(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")


# ---------------------------------------------------------------------------
# D. EMAIL TESTS
# ---------------------------------------------------------------------------
# Your view does NOT call send_mail() anywhere, so no confirmation email is
# ever sent. These tests document that behaviour. Django's test runner already
# swaps the real email backend for an in-memory one, so mail.outbox is safe.

class EmailBehaviourTests(TestCase):

    def setUp(self):
        self.url = reverse("register_institutional")

    def test_no_email_is_sent_after_valid_registration(self):
        self.client.post(self.url, valid_data())
        self.assertEqual(len(mail.outbox), 0)

    def test_no_email_is_sent_after_invalid_registration(self):
        self.client.post(self.url, valid_data(email="not-an-email"))
        self.assertEqual(len(mail.outbox), 0)

    def test_no_email_is_sent_on_page_load(self):
        self.client.get(self.url)
        self.assertEqual(len(mail.outbox), 0)
