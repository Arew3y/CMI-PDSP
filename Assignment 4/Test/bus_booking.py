class BusBooking:
    def __init__(self):
        self.esw_number = 20  # Number of empty window seats
        self.esw_list = []  # List of empty window seat numbers
        self.esa_number = 20  # Number of empty aisle seats
        self.esa_list = []  # List of empty aisle seat numbers

        self.seats = {}  # Tracks booking_id for each seat (e.g., "W1": 1, "A1": 0)
        self.seat_holders = {}  # Tracks the allotted seat for each booking_id (e.g., 1: "W1")

        self.waiting = []  # Waiting list for unalloted bookings
        self.no_of_waiting = 0  # Count of bookings in waiting list

        self.no_of_bookings = 0  # Counter for generating unique booking_id
        self.bookings = {}  # Stores the name for each booking_id (e.g., 1: "John")

        for i in range(20):  # Populating the seats dict and lists with 40 seats
            w = str("W" + str(i + 1))
            a = str("A" + str(i + 1))
            self.seats[w] = 0  # 0 means the seat is empty
            self.seats[a] = 0
            self.esw_list.append(w)
            self.esa_list.append(a)
        #

    def book(self, name, preference):
        pref = 0  # Default pref (0) means no preference
        self.no_of_bookings += 1
        booking_id = self.no_of_bookings  # Use the total count as a unique booking_id

        status = None
        seat_number = None

        # Parsing seat preferences: 1 for window, 2 for aisle
        if preference == 'W' or preference == 'w' or preference == 'Window' or preference == 'window':
            pref = 1
        elif preference == 'A' or preference == 'a' or preference == 'Aisle' or preference == 'aisle':
            pref = 2

        # Handle booking if seats are available
        if self.esw_number > 0 or self.esa_number > 0:
            if pref == 1 or pref == 0:  # Preference is Window or No Preference
                if self.esw_number > 0:  # Window preference available
                    seat_number = self.esw_list.pop(0)
                    self.esw_number -= 1
                elif self.esa_number > 0:  # Window not available, give aisle
                    seat_number = self.esa_list.pop(0)
                    self.esa_number -= 1
            elif pref == 2:  # Preference is Aisle
                if self.esa_number > 0:  # Aisle preference available
                    seat_number = self.esa_list.pop(0)
                    self.esa_number -= 1
                elif self.esw_number > 0:  # Aisle not available, give window
                    seat_number = self.esw_list.pop(0)
                    self.esw_number -= 1

            # Update all tracking dictionaries
            self.seats[seat_number] = booking_id
            self.seat_holders[booking_id] = seat_number
            self.bookings[booking_id] = name
            status = str(seat_number)
        else:
            # Handle booking if no seats are available (add to waiting list)
            self.waiting.append((booking_id, name))
            self.no_of_waiting += 1
            status = str("WL-" + str(self.no_of_waiting))
            self.bookings[booking_id] = name

        return booking_id, status
        #

    def cancel(self, booking_id):
        # Case 1: Booking to cancel has a confirmed seat
        if booking_id in self.seat_holders.keys():
            temp_seat = self.seat_holders[booking_id]
            del self.seat_holders[booking_id]

            # Allot this seat to the next person in the waiting list
            if self.no_of_waiting > 0:
                new_passenger = self.waiting.pop(0)
                self.seats[temp_seat] = new_passenger[0]
                self.no_of_waiting -= 1
                self.seat_holders[new_passenger[0]] = temp_seat
            else:
                # No one is waiting, so mark the seat as empty
                self.seats[temp_seat] = 0
                if temp_seat[0] == "W":
                    self.esw_number += 1
                    self.esw_list.append(temp_seat)
                elif temp_seat[0] == "A":
                    self.esa_number += 1
                    self.esa_list.append(temp_seat)
            return True

        # Case 2: Booking to cancel is in the waiting list
        waiting_status = False
        v = (None, None)
        for v1, v2 in self.waiting:
            if v1 == booking_id:  # Find the booking in the waiting list
                waiting_status = True
                v = (v1, v2)
                break

        if waiting_status:
            self.waiting.remove(v)
            self.no_of_waiting -= 1
            return True

        return False  # Booking ID was not found anywhere
        #

    def status(self, booking_id):
        waiting_status = False
        i = None

        # Case 1: Booking has a confirmed seat
        if booking_id in self.seat_holders.keys():
            return self.bookings[booking_id], self.seat_holders[booking_id]

        # Case 2: Booking is in the waiting list
        for v1, v2 in self.waiting:
            if v1 == booking_id:
                waiting_status = True
                i = self.waiting.index((v1, v2))  # Get the index (position) in the waiting list
                break

        if waiting_status:
            status = str("WL-" + str(i + 1))  # WL-1, WL-2, etc.
            return self.bookings[booking_id], status

        return None, None  # Booking ID not found
        #

    def __str__(self):
        lst = []
        for booking_id in self.bookings.keys():
            name, status = self.status(booking_id)
            if status is not None:  # Filter out cancelled bookings that were not found
                lst.append((str(booking_id), str(name), str(status)))

        lst.sort(key=lambda x: x[0])  # Sort the list based on booking ID
        return str(lst)