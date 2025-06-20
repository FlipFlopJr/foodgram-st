import json

from django.core.management.base import BaseCommand
from django.db import transaction

from recipes.models import IngredientModel


class Command(BaseCommand):
    help = "Import ingredients from a JSON file"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="JSON file path")

    def handle(self, *args, **options):
        file_path = options["file_path"]

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            with transaction.atomic():
                ingredients = [
                    IngredientModel(
                        name=item["name"].lower(),
                        measurement_unit=item["measurement_unit"].lower(),
                    )
                    for item in data
                ]

                IngredientModel.objects.bulk_create(
                    ingredients,
                    ignore_conflicts=True,
                )

            total_amount_ingredients = len(ingredients)
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Loaded {total_amount_ingredients} ingredients successfully"
                )
            )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Oops! We couldn’t find {file_path}"))
        except json.JSONDecodeError:
            self.stdout.write(
                self.style
                .ERROR(f"We couldn't read {file_path} - "
                       f"it's not in the correct JSON format.")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error loading ingredients: {str(e)}")
            )
