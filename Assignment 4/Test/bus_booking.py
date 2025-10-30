class BusBooking:
    def __init__(self):
        self.esw_number = 20          # Int variable holding the number of empty window seats
        self.esw_list = []            # List holding the empty window seat numbers
        self.esa_number = 20          # Int variable holding the number of empty aisle seats
        self.esa_list = []            # List holding the empty window aisle numbers

        self.seats = {}               # Creating a dictionary of seats as keys and the booking_id as values.
        self.seat_holders = {}        # Dict of all the booking_id's with an alloted seat

        self.waiting = []             # Waiting list for unalloted bookings
        self.no_of_waiting = 0        # A count for number of bookings waiting

        self.no_of_bookings = 0       # A count to keep the count of number of unique bookings
        self.bookings = {}            # Dict of all the bookings

        for i in range(20):           # Populating the seats dict and lists with the Seat numbers
            w = str("W" + str(i+1))   # Making seat numbers
            a = str("A" + str(i+1))
            self.seats[w] = 0
            self.seats[a] = 0
            self.esw_list.append(w)
            self.esa_list.append(a)
        #
    def book(self, name, preference):
        pref = 0
        self.no_of_bookings += 1
        booking_id = self.no_of_bookings
        status = None
        seat_number = None

        if preference == 'W' or preference == 'w' or preference == 'Window' or preference == 'window':
            pref = 1
        elif preference == 'A' or preference == 'a' or preference == 'Aisle' or preference == 'aisle':
            pref = 2

        if self.esw_number > 0 or self.esa_number > 0:
            if pref == 1 or pref == 0:
                if self.esw_number > 0:
                    seat_number = self.esw_list[0]
                    self.esw_list.pop(0)
                    self.esw_number -= 1
                elif self.esa_number > 0:
                    seat_number = self.esa_list[0]
                    self.esa_list.pop(0)
                    self.esa_number -= 1
            elif pref == 2 or pref == 0:
                if self.esa_number > 0:
                    seat_number = self.esa_list[0]
                    self.esa_list.pop(0)
                    self.esa_number -= 1
                elif self.esw_number > 0:
                    seat_number = self.esw_list[0]
                    self.esw_list.pop(0)
                    self.esw_number -= 1
            self.seats[seat_number] = booking_id
            self.seat_holders[booking_id] = seat_number
            self.bookings[booking_id] = name
            status = str(seat_number)
        else:
            self.waiting.append((booking_id,name))
            self.no_of_waiting += 1
            status = str("WL-" + str(self.no_of_waiting))
            self.bookings[booking_id] = name

        return booking_id, status
        #
    def cancel(self, booking_id):
        if booking_id in self.seat_holders.keys():
            temp_seat = self.seat_holders[booking_id]
            del self.seat_holders[booking_id]

            if self.no_of_waiting > 0:
                new_passenger = self.waiting[0]
                self.seats[temp_seat] = new_passenger[0]
                self.waiting.pop(0)
                self.no_of_waiting -= 1
                self.seat_holders[new_passenger[0]] = temp_seat
            else:
                self.seats[temp_seat] = 0
                if temp_seat[0] == "W":
                    self.esw_number += 1
                    self.esw_list.append(temp_seat)
                elif temp_seat[0] == "A":
                    self.esa_number += 1
                    self.esa_list.append(temp_seat)
            return True

        waiting_status = False
        v = (None, None)
        for v1, v2 in self.waiting:
            if v1 == booking_id:
                waiting_status = True
                v = (v1, v2)
                break

        if waiting_status:
            self.waiting.remove(v)
            self.no_of_waiting -= 1
            return True

        return False
        #
    def status(self, booking_id):
        waiting_status = False
        i = None

        if booking_id in self.seat_holders.keys():
            return self.bookings[booking_id],self.seat_holders[booking_id]

        for v1, v2 in self.waiting:
            if v1 == booking_id:
                waiting_status = True
                i = self.waiting.index((v1, v2))
                break

        if waiting_status:
            status = str("WL-" + str(i+1))
            return self.bookings[booking_id], status

        return None, None
        #
    def __str__(self):
        lst = []
        for booking_id in self.bookings.keys():
            name, status = self.status(booking_id)
            if status is not None:
                lst.append((str(booking_id), str(name), str(status)))
        lst.sort(key=lambda x: x[0])
        return str(lst)