"""Pharmacy prescription and stock tracker used for Lab 5 static analysis."""

import json
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

DATABASE = ":memory:"
STOCK_FILE = Path("stock.json")
PRESCRIPTIONS_FILE = Path("prescriptions.json")

connection = sqlite3.connect(DATABASE)
stock: dict[str, dict[str, Any]] = {}
prescriptions: list[dict[str, Any]] = []


def setup_database() -> None:
    """Create and populate the small in-memory patient database."""
    with connection:
        connection.execute(
            "CREATE TABLE patients (id TEXT PRIMARY KEY, name TEXT NOT NULL, "
            "allergy TEXT NOT NULL)"
        )
        connection.executemany(
            "INSERT INTO patients (id, name, allergy) VALUES (?, ?, ?)",
            [
                ("P1", "Kavya", "penicillin"),
                ("P2", "Arjun", "none"),
                ("P3", "Meena", "ibuprofen"),
            ],
        )


def find_patient(name: str) -> list[tuple[str, str]]:
    """Return the patient ID and allergy for an exact, case-insensitive name."""
    with connection:
        cursor = connection.execute(
            "SELECT id, allergy FROM patients WHERE name = ? COLLATE NOCASE",
            (name.strip(),),
        )
        return cursor.fetchall()


def add_stock(
    drug: str, units: int, expiry: str, batch_log: list[tuple[str, int]] | None = None
) -> int:
    """Add medicine units and return the number of recorded batches."""
    if units <= 0:
        raise ValueError("Stock units must be a positive integer.")
    expiry_date = date.fromisoformat(expiry)
    if not drug.strip():
        raise ValueError("Medicine name cannot be empty.")

    current = stock.get(drug, {})
    stock[drug] = {
        "units": current.get("units", 0) + units,
        "expiry": expiry_date.isoformat(),
    }
    if batch_log is None:
        batch_log = []
    batch_log.append((drug, units))
    return len(batch_log)


def dispense(patient_name: str, drug: str, units: int) -> bool:
    """Dispense medicine only when the patient, stock, and allergy checks pass."""
    if units <= 0:
        print("Dispense quantity must be positive.")
        return False

    patients = find_patient(patient_name)
    if not patients:
        print(f"Patient not found: {patient_name}")
        return False

    patient_id, allergy = patients[0]
    allergy_terms = {
        term.strip().casefold()
        for term in allergy.split(",")
        if term.strip() and term.strip().casefold() != "none"
    }
    if drug.casefold() in allergy_terms:
        print(f"Allergy warning for {patient_name}: {drug}")
        return False

    medicine = stock.get(drug)
    if medicine is None:
        print(f"Medicine not found: {drug}")
        return False
    if medicine["units"] < units:
        print(f"Insufficient stock for {drug}. Available: {medicine['units']}")
        return False

    expiry_date = date.fromisoformat(medicine["expiry"])
    if expiry_date < date.today():
        print(f"Cannot dispense expired medicine: {drug}")
        return False

    medicine["units"] -= units
    prescriptions.append(
        {
            "patient": patient_id,
            "drug": drug,
            "units": units,
            "time": datetime.now().isoformat(timespec="seconds"),
        }
    )
    return True


def expiring_soon(days: int = 30) -> list[str]:
    """Return non-expired medicines expiring within the next number of days."""
    if days < 0:
        raise ValueError("Days must be zero or greater.")
    today = date.today()
    cutoff = today + timedelta(days=days)
    soon = []
    for drug, details in stock.items():
        expiry_date = date.fromisoformat(details["expiry"])
        if today <= expiry_date <= cutoff:
            soon.append(drug)
    return sorted(soon)


def export_prescriptions(file: str | Path = PRESCRIPTIONS_FILE) -> None:
    """Write prescription records as formatted JSON."""
    with Path(file).open("w", encoding="utf-8") as output_file:
        json.dump(prescriptions, output_file, indent=2)


def load_stock(file: str | Path = STOCK_FILE) -> None:
    """Load saved stock data when the file exists and contains valid JSON."""
    path = Path(file)
    if not path.exists():
        return
    try:
        with path.open("r", encoding="utf-8") as input_file:
            loaded_stock = json.load(input_file)
    except (OSError, json.JSONDecodeError) as error:
        print(f"Could not load stock from {path}: {error}")
        return

    if not isinstance(loaded_stock, dict):
        print(f"Could not load stock from {path}: expected a JSON object.")
        return
    for drug, details in loaded_stock.items():
        if (
            isinstance(drug, str)
            and isinstance(details, dict)
            and isinstance(details.get("units"), int)
            and details["units"] >= 0
            and isinstance(details.get("expiry"), str)
        ):
            try:
                date.fromisoformat(details["expiry"])
            except ValueError:
                continue
            stock[drug] = {
                "units": details["units"],
                "expiry": details["expiry"],
            }


def print_stock() -> None:
    """Print the current medicine inventory."""
    print("Pharmacy Stock")
    for drug, details in sorted(stock.items()):
        print(
            f"{drug} -> {details['units']} units, "
            f"expires {details['expiry']}"
        )


def main() -> None:
    """Run the demonstration workflow."""
    load_stock()

    add_stock("Paracetamol", 100, "2027-03-01")
    add_stock("Amoxicillin", 20, "2027-12-31")
    add_stock("Penicillin", 50, "2027-01-15")
    add_stock("Ibuprofen", 15, "2026-11-30")

    print("Arjun gets Amoxicillin:", dispense("Arjun", "Amoxicillin", 30))
    print("Kavya gets Penicillin:", dispense("Kavya", "Penicillin", 10))
    print("Meena gets ibuprofen:", dispense("Meena", "Ibuprofen", 2))
    print("Unknown patient:", dispense("Ghost", "Paracetamol", 5))

    name = input("Patient name to look up (Enter for Arjun): ").strip() or "Arjun"
    print("Lookup result:", find_patient(name))
    print("Expiring within 30 days:", expiring_soon())
    export_prescriptions()
    print_stock()


if __name__ == "__main__":
    setup_database()
    try:
        main()
    finally:
        connection.close()
