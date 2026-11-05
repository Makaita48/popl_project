"""CSC1101 Case 8: Student Hostel Room Allocation System.

Run this file in Python using VS Code or a terminal.
Only Python's standard library is needed; there are no packages to install.
The program creates hostel_data.txt beside this file when saving.
Each student has one line: Student ID|Name|Gender|Room
For example: 260685|Muzi Ncube|Male|A101
A dash (-) in the Room field means the student has not been allocated.

The six rooms below are demonstration rooms, not official university records.
Sample block A is for male students and sample block B is for female students.
"""

from pathlib import Path


# Keep saved records beside the program, even when run from another folder.
DATA_FILE = Path(__file__).with_name("hostel_data.txt")


def required_text(value, label):
    """Check text entered by staff or read from the saved file."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(label + " must contain text.")
    # These characters separate fields and records in our text file.
    if "|" in value or "\n" in value or "\r" in value:
        raise ValueError(label + " cannot contain | or a line break.")
    return value.strip()


class Student:
    """One student and the details needed for room allocation."""

    def __init__(self, student_id, name, gender):
        self.student_id = required_text(student_id, "Student ID").upper()
        self.name = required_text(name, "Student name")

        # Accept short answers as well as full words.
        genders = {"m": "Male", "male": "Male", "f": "Female", "female": "Female"}
        answer = required_text(gender, "Gender").lower()
        if answer not in genders:
            raise ValueError("Enter M for male or F for female.")
        self.gender = genders[answer]
        self.block = "A" if self.gender == "Male" else "B"


class Room:
    """The parent class contains details shared by all room types."""

    def __init__(self, room_id, block):
        self.room_id = room_id
        self.block = block
        self.student_ids = []  # Store the IDs of students in this room.

    def get_capacity(self):
        # The child classes below supply their own version of this method.
        raise NotImplementedError("Use a single, double or triple room.")

    def has_space(self):
        return len(self.student_ids) < self.get_capacity()

    def get_status(self):
        if len(self.student_ids) == 0:
            return "EMPTY"
        if not self.has_space():
            return "FULL"
        return "PARTLY FILLED"

    def add_student(self, student_id):
        if student_id in self.student_ids:
            raise ValueError("This student is already in this room.")
        if not self.has_space():
            raise ValueError("This room is full. Choose another room.")
        self.student_ids.append(student_id)


# Inheritance: each of these classes receives Room's shared methods.
# Method overriding: each supplies a different get_capacity() method.
class SingleRoom(Room):
    def get_capacity(self):
        return 1


class DoubleRoom(Room):
    def get_capacity(self):
        return 2


class TripleRoom(Room):
    def get_capacity(self):
        return 3


class Hostel:
    """Manage students, rooms and the rules for allocating beds."""

    def __init__(self):
        self.students = []
        # Start with sample rooms to keep setup and the class demo simple.
        # Room IDs must be unique. A = male block; B = female block.
        self.rooms = [
            SingleRoom("A101", "A"),
            DoubleRoom("A102", "A"),
            TripleRoom("A103", "A"),
            SingleRoom("B101", "B"),
            DoubleRoom("B102", "B"),
            TripleRoom("B103", "B"),
        ]

    def find_student(self, student_id):
        for student in self.students:
            if student.student_id == student_id:
                return student
        return None

    def find_room(self, room_id):
        for room in self.rooms:
            if room.room_id == room_id:
                return room
        return None

    def find_student_room(self, student_id):
        # Check every room, so a student cannot receive a second allocation.
        for room in self.rooms:
            if student_id in room.student_ids:
                return room
        return None

    def register_student(self, student_id, name, gender):
        student = Student(student_id, name, gender)
        if self.find_student(student.student_id) is not None:
            raise ValueError("That student ID is already registered.")
        self.students.append(student)

    def allocate_student(self, student_id, room_id):
        student_id = required_text(student_id, "Student ID").upper()
        room_id = required_text(room_id, "Room ID").upper()
        student = self.find_student(student_id)
        room = self.find_room(room_id)

        # Check every rule before changing the room's occupant list.
        if student is None:
            raise ValueError("Student not found. Register the student first.")
        if room is None:
            raise ValueError("Room not found. Use a room ID shown in the list.")
        current_room = self.find_student_room(student_id)
        if current_room is not None:
            raise ValueError("Student is already allocated to " + current_room.room_id + ".")
        if student.block != room.block:
            raise ValueError("This student needs a room in block " + student.block + ".")
        room.add_student(student_id)  # Also checks that the room has space.

    def show_rooms(self):
        print("\nROOM STATUS   |   Block A: Male   |   Block B: Female")
        print(f"{'Room':<8}{'Block':<8}{'Type':<14}{'Beds used':<12}Status")
        for room in self.rooms:
            # Capacity selects the label for the screen display.
            room_type = {1: "Single", 2: "Double", 3: "Triple"}[room.get_capacity()]
            beds = str(len(room.student_ids)) + "/" + str(room.get_capacity())
            print(f"{room.room_id:<8}{room.block:<8}{room_type:<14}{beds:<12}{room.get_status()}")

    def show_allocations(self):
        if not self.students:
            print("No students are registered yet.")
            return
        print("\nSTUDENT ALLOCATIONS")
        for student in self.students:
            room = self.find_student_room(student.student_id)
            result = room.room_id if room is not None else "Not allocated"
            print(f"{student.student_id} | {student.name} | {student.gender} | {result}")


def save_data(hostel):
    """Write one student per line, with fields separated by |."""
    # Finish writing a temporary file before replacing the previous save.
    # If writing fails, the previous data file is kept.
    temporary_file = DATA_FILE.with_suffix(".tmp")
    with open(temporary_file, "w", encoding="utf-8") as file:
        file.write("Student ID|Name|Gender|Room\n")
        for student in hostel.students:
            room = hostel.find_student_room(student.student_id)
            room_id = room.room_id if room is not None else "-"
            file.write(f"{student.student_id}|{student.name}|{student.gender}|{room_id}\n")
    temporary_file.replace(DATA_FILE)


def load_data():
    """Read the text file and rebuild students and allocations."""
    hostel = Hostel()
    try:
        file = open(DATA_FILE, "r", encoding="utf-8")
    except FileNotFoundError:
        print("First run: starting with the six sample rooms and no students.")
        return hostel

    # 'with' closes the file automatically, even if a record is invalid.
    with file:
        if file.readline().strip() != "Student ID|Name|Gender|Room":
            raise ValueError("The text file heading is missing or incorrect.")
        for line_number, line in enumerate(file, start=2):
            if not line.strip():
                continue  # Ignore empty lines.
            fields = line.strip().split("|")
            if len(fields) != 4:
                raise ValueError(f"Line {line_number} must contain four fields separated by |.")
            student_id, name, gender, room_id = fields
            hostel.register_student(student_id, name, gender)
            if room_id.strip() != "-":
                # Reuse our checks for correct blocks, duplicates and room space.
                hostel.allocate_student(student_id, room_id)
    return hostel


def save_or_warn(hostel):
    """Report a failed save without losing the records still in memory."""
    try:
        save_data(hostel)
        print("Records saved.")
        return True
    except (OSError, UnicodeError) as error:
        print("Could not save:", error)
        print("Changes are still in memory. Keep the program open and try saving again.")
        return False


def main():
    try:
        hostel = load_data()
    except (OSError, ValueError) as error:
        print("Could not load hostel_data.txt:", error)
        print("The existing file has been kept unchanged. Correct it before restarting.")
        return

    while True:
        try:
            print("\nHOSTEL ROOM ALLOCATION")
            print("1. Register a student")
            print("2. View rooms and available space")
            print("3. Allocate a student to a room")
            print("4. View student allocations")
            print("5. Save records")
            print("0. Save and exit")
            choice = input("Choose an option: ").strip()

            if choice == "1":
                student_id = input("Student ID: ")
                name = input("Full name: ")
                gender = input("Gender (M/F): ")
                hostel.register_student(student_id, name, gender)
                print("Student registered.")
                save_or_warn(hostel)
            elif choice == "2":
                hostel.show_rooms()
            elif choice == "3":
                hostel.show_rooms()
                student_id = input("Student ID: ")
                room_id = input("Room ID: ")
                hostel.allocate_student(student_id, room_id)
                print("Room allocated successfully.")
                save_or_warn(hostel)
            elif choice == "4":
                hostel.show_allocations()
            elif choice == "5":
                save_or_warn(hostel)
            elif choice == "0":
                if save_or_warn(hostel):
                    print("Goodbye.")
                    return
            else:
                print("Invalid option. Choose 0, 1, 2, 3, 4 or 5.")
        except ValueError as error:
            # A rejected entry returns to the menu without changing allocations.
            print("Cannot complete this action:", error)
        except KeyboardInterrupt:
            print("\nInput cancelled. Use option 0 to save and exit.")
        except EOFError:
            # A closed input stream cannot accept another menu choice.
            print("\nInput has closed. Attempting to save before stopping.")
            if not save_or_warn(hostel):
                print("The latest changes could not be saved.")
            return


# Importing the file for testing will not start the interactive menu.
if __name__ == "__main__":
    main()
