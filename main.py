import random
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

colorama_init()

class Sector:
    def __init__(self, type_name):
        self.type_name = type_name

    class Facility:
        def __init__(self, name, price, owner=None):
            self.name = name
            self.price = price
            self.owner = None
            self.level = 0
            self.level_prices = (100, 200, 400)

        def level_up(self) -> bool:
            if self.level < 3:
                self.level += 1
                self.price *= 1.5
                print(f"{Fore.GREEN}Facility '{self.name}' was upped to {self.level} level. Now its price is {self.price}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.YELLOW}Facility {self.name} already have max level{Style.RESET_ALL}")
                return False

        def __str__(self):
            return f"{self.name} | ₴{self.price} [{self.level if self.level < 3 else str(self.level)+'|max'}] {'{'}{self.owner.name if self.owner else 'no owner'}{'}'}"

    class MoneySector:
        def __init__(self, price):
            self.price = price
            if price < 0:
                self.name = f'Fire'
            else:
                self.name = f'Fortune'

        def __str__(self):
            return f"{self.name} | ₴{self.price}"


class Field:
    def __init__(self, all_sectors):
        global PLAYERS
        # self.facilities = facilities
        # self.money_sectors = money_sectors
        # self.all_sectors = self.make_all_sectors(facilities, money_sectors)
        self.all_sectors = all_sectors
        self.field_sectors_pos = [3, 7, 8, 4, 5, 9, 10, 1, 6, 2, 11]

    @staticmethod
    def make_all_sectors(facilities, money_sectors):
        all_sectors = {}
        c = 0
        for fac in facilities:
            for i in fac:
                c += 1
                all_sectors[str(c)] = i
        for ms in money_sectors:
            for j in ms:
                c += 1
                all_sectors[str(c)] = j
        return all_sectors

    def get_sector(self, index):
        if TEST:
            return self.all_sectors[str(index)]
        else:
            return self.all_sectors[str(self.field_sectors_pos[index-1])]

    def show_field(self, players):
        print('', f'{Fore.BLUE} FIELD {Style.RESET_ALL}', '', sep='_'*26)
        for p_info in players:
            if p_info[1].playable:
                if p_info[1].position == 0:
                    print(f'{Fore.BLUE}__{p_info[0]}_{Style.RESET_ALL}')
                else:
                    print(' '*5 * p_info[1].position, f'{Fore.BLUE}__{p_info[0]}_{Style.RESET_ALL}', sep='')

        # print("[ 0]-[ 1]-[ 2]-[ 3]-[ 4]-[ 5]-[ 6]-[ 7]-[ 8]-[ 9]-[10]-[11]")
        print(f"{Fore.BLUE}[ 0]", end='')
        for i in self.field_sectors_pos:
            print(f"-[{f' {i}' if i<10 else i}]", end='')
        print(f'{Style.RESET_ALL}')

    def show_info(self):
        def print_sector(sector, index='0'):
            print(f'{index}.', sector, sep=('  ' if int(index) < 10 else ' '))

        print('', ' LEGEND ', '', sep='_' * 11)
        for index, sector in self.all_sectors.items():
            print_sector(sector, index)

        # print('', ' LEGEND ', '', sep='_'*11)
        # print('', '-- FACILITIES --', '', sep=' '*7)
        # index = 0
        # for fracs in self.facilities:
        #     for f in fracs:
        #         index += 1
        #         print_sector(f, index)
        # print('', '-- MONEY SECTOR --', '', sep=' '*6)
        # for sectors in self.money_sectors:
        #     for s in sectors:
        #         index += 1
        #         print_sector(s, index)


class Player:
    def __init__(self, name, balance=0):
        self.name = name
        self.balance = balance
        self.facility_own_set = {}
        self.playable = True
        self.position = 0

    def buy_facility(self, facility):
        # якщо гравець є власником
        if facility.owner == self:
            print(f'{Fore.GREEN}You on own facility. Pass.{Style.RESET_ALL}')
            return

        # перевірка балансу
        if self.balance >= facility.price:
            pass
        else:
            # перевірка чи гравець взагалі спроможний покрити витрати
            if self.sum_amount_own_facilities() + self.balance >= facility.price:
                while True:
                    print(f"{Fore.YELLOW}You don't have enough money.{Style.RESET_ALL}")
                    if self.sum_amount_own_facilities() >= self.balance:
                        self.show_info()
                        self.sell_facility(input(f"{Fore.YELLOW}Try to sell some own facilities. {p[1].name}, enter number: {Style.RESET_ALL}"))
                    if self.balance >= facility.price:
                        print(f'{Fore.GREEN}Now you have enough money to buy/rent.{Style.RESET_ALL}')
                        break
            else:
                # оголосити програш гравця
                print(f"{Fore.YELLOW}You don't have enough money, even you sold all your facilities.{Style.RESET_ALL}{Fore.RED}\n{self.name}, YOU LOSE!{Style.RESET_ALL}")
                self.sell_facility('0', player_lose=True)   # повернути всі бізнеси
                self.playable = False   # позначити як поза грою
                global COUNT_OF_PLAYABLE_PLAYERS
                COUNT_OF_PLAYABLE_PLAYERS -= 1
                return

        # якщо власника немає
        if facility.owner is None:
            facility.owner = self
            self.facility_own_set[str(len(self.facility_own_set)+1)] = facility
            self.balance -= facility.price
            print(f"{Fore.GREEN}You just bought facility '{facility.name}' for ₴{facility.price}.{Style.RESET_ALL}")
            return

        # якщо власником є інший гравець
        if facility.owner is not None:
            facility.owner.balance += facility.price
            self.balance -= facility.price
            print(f"{Fore.GREEN}{facility.owner.name} got ₴{facility.price} rent from {self.name}{Style.RESET_ALL}")
            return

    def sell_facility(self, index, player_lose=False):
        if not self.facility_own_set:
            print(f"{Fore.RED}{self.name}, you don't have any own facility!{Style.RESET_ALL}") if not player_lose else None
            return

        if player_lose:     # на випадок, якщо гравець програв
            for i, f in self.facility_own_set.items():
                f.owner = None
            self.facility_own_set = {}
            return

        # продаж бізнесу
        try:
            global SELLING_FACILITIES_CUT
            self.balance += self.facility_own_set[index].price * SELLING_FACILITIES_CUT
            print(f"{Fore.GREEN}{self.name} sold '{self.facility_own_set[index].name}' for ₴{self.facility_own_set[index].price * SELLING_FACILITIES_CUT}{Style.RESET_ALL}")
            self.facility_own_set[index].owner = None
            del self.facility_own_set[index]
        except KeyError:
            print(f'{Fore.RED}Wrong number of own facility, try again.{Style.RESET_ALL}')

    def choose_sector(self, sector):
        if type(sector) == Sector.Facility:         # якщо це сектор бізнесу
            print(f"{Fore.GREEN}That is facility sector. {Style.RESET_ALL}", end='')
            self.buy_facility(sector)
        elif type(sector) == Sector.MoneySector:    # якщо це грошовий сектор
            print(f"{Fore.GREEN}That is money sector. You {'lost' if sector.price < 0 else 'got'} ₴{sector.price}{Style.RESET_ALL}")
            self.balance += sector.price

    def level_up_facility(self, index):
        if self.facility_own_set:   # перевірка чи гравець взагалі має бізнеси
            try:
                if self.facility_own_set[index].level > 2:  # перевірка чи бізнес вже має макс рівень
                    print(f"{Fore.YELLOW}Facility {self.facility_own_set[index].name} already have max level.{Style.RESET_ALL} (sms from level_up_facility())")
                    return
            except KeyError:
                print('agagdfgssgsgsgfsg')

            try:
                if self.balance >= self.facility_own_set[index].level_prices[self.facility_own_set[index].level]:
                    while True:
                        o = input(f'Level will cost {Fore.BLUE}₴{self.facility_own_set[index].level_prices[self.facility_own_set[index].level]}{Style.RESET_ALL}. Do you want to continue? (1/0): ')
                        if o == '1':
                            temp_level = self.facility_own_set[index].level
                            if self.facility_own_set[index].level_up():
                                self.balance -= self.facility_own_set[index].level_prices[temp_level]
                                return
                            else:
                                return
                        elif o == '0':
                            return
                        else:
                            continue

                else:
                    print(f"{Fore.RED}You don't have enough money to up level! It cost ₴{self.facility_own_set[index].level_prices[self.facility_own_set[index].level]}.{Style.RESET_ALL}")
            except KeyError:
                print(f'{Fore.RED}Wrong number of own facility, try again.{Style.RESET_ALL}')
        else:
            # raise ValueError(f"Player {self.name} don't have any facility")
            print(f"Player {self.name} don't have any facility")

    def sum_amount_own_facilities(self):
        summed = 0
        for index, f in self.facility_own_set.items():
            summed += self.facility_own_set[index].price
        return summed

    def show_info(self):
        if self.playable:
            print(f"{self.name} - ₴{self.balance}")
            print(f"Own facilities:", end=' ')
            for index, f in self.facility_own_set.items():
                print(f"{Fore.BLUE}[{index}|{f.name}]{Style.RESET_ALL}", end=(', ' if len(self.facility_own_set) > 1 else ''))
            print()
        else:
            print(f"{self.name} - {Fore.GREEN}OUT{Style.RESET_ALL}")


cars = Sector('Car Industry')         # Сектори Автоіндустрії
energy = Sector('Energy Industry')    # Сектори Енергетики
fires = Sector('Fire Sector')         # Сектори штрафів (програш грошей)
fortunes = Sector('Fortune Sector')   # Сектори фортуни (виграш грошей)
ALL_SECTORS = {
    # бізнеси | facilities
    '1': cars.Facility('VW', 200),
    '2': cars.Facility('Toyota', 150),
    '3': cars.Facility('GM', 100),
    '4': energy.Facility('Atomic energy', 200),
    '5': energy.Facility('Solar energy', 150),
    '6': energy.Facility('Wind energy', 100),
    # штрафи та фортуни
    '7': fires.MoneySector(-400),
    '8': fires.MoneySector(-200),
    '9': fires.MoneySector(-100),
    '10': fortunes.MoneySector(400),
    '11': fortunes.MoneySector(100)
}
field = Field(ALL_SECTORS)  # утворення поля

""" ========================= НАЛАШТУВАННЯ  ========================= """
PLAYERS = [('A', Player('Alex', balance=200)), ('B', Player('Vlad', balance=2000))]    # гравці
SELLING_FACILITIES_CUT = 0.75   # КОМІСІЯ за продаж бізнесу (відсоток, який дістанеться продавцю)
TEST = False        # ТЕСТОВИЙ РЕЖИМ. Можна купляти любий бізнес по його ID
CUBE_CHEAT = True   # ЧІТИ НА КУБИК. Можна вписати число для кубика
""" ================================================================= """

iteration = 0
COUNT_OF_PLAYABLE_PLAYERS = len(PLAYERS)
game_loop = True
while game_loop:
    print('\n', "/"*60, '\t'*6+'NEW ROUND', '='*60, sep='\n')
    iteration += 1
    for p in PLAYERS:
        # закінчення гри та визначення переможця
        if COUNT_OF_PLAYABLE_PLAYERS <= 1:
            for i in PLAYERS:
                print(f"\n  = PLAYER {i[1].name} WIN =") if i[1].playable else ''
            print("\t == GAME OVER ==")
            game_loop = False
            break

        if p[1].playable:   # перевірка чи гравець не вибув з гри
            iteration_loop = True
            have_posibility_to_through_cube = True

            # ХІД ГРАВЦЯ
            while iteration_loop:
                field.show_info()   # показати інформацію про поле
                print()
                for pl in PLAYERS:
                    print(f"PLAYER {pl[0]}: ", end='')
                    pl[1].show_info()
                field.show_field(PLAYERS)   # показати поле

                print(f"\t\t---------- MENU ----------\n\t\t1 - {'Make iteration' if TEST else 'Trough cubes'}\n\t\t2 - Sell facility\n\t\t3 - Level up own facility\n\t\t0 - EXIT (end iteration)")
                print('\n', f' Iter {iteration} ', '', sep='_'*11)
                choice = int(input(f"Player, {p[1].name}. Make choice: "))  # вибір гравця в меню

                # 1 - Кинути кубик | Якщо TEST, то вибрати бізнес для покупки
                if choice == 1:
                    if TEST:
                        p[1].choose_sector(field.get_sector(input(f"{p[1].name}, choose sector: ")))    # вибрати бізнес для покупки
                    else:
                        if have_posibility_to_through_cube: # перевірка чи гравець вже кидав кубик
                            # КИДОК КУБИКА
                            cube_number = (input(f'{Fore.CYAN}(CUBE_CHEAT ENABLE){Style.RESET_ALL} Enter cube number: ') if CUBE_CHEAT else random.randint(1, 4))
                            try:
                                cube_number = int(cube_number)
                                if cube_number > 12 or cube_number <= 0:
                                    print(f'{Fore.RED}Cube number too huge or is negative! Please, use numbers 1-12{Style.RESET_ALL}')
                                    continue
                            except ValueError:
                                raise ValueError(f'{Fore.CYAN}\n\tЗАРАЗ АКТИВНИЙ ЧІТ НА КУБИК.\n\tБУДЬ ЛАСКА, ВВОДЬТЕ ЛИШЕ ЧИСЛА ДЛЯ ЦЬОГО ЧІТА{Style.RESET_ALL}')

                            print(f'{Fore.BLUE}\tCUBE NUMBER =', cube_number, f'{Style.RESET_ALL}')
                            if cube_number <= 11 - p[1].position:   # перевірка чи число кубика не перевищує відстань від позиції до кінця поля
                                # якщо число менше, то просто додати хід
                                p[1].choose_sector(field.get_sector(p[1].position + cube_number))
                                p[1].position += cube_number
                            else:
                                # якщо число більше, то перекинути на початок поля
                                p[1].position = cube_number - (11 - p[1].position)
                                p[1].choose_sector(field.get_sector(p[1].position))
                            have_posibility_to_through_cube = False
                        else:
                            # print('You already though cube! Try another menu action.')
                            print(f'{Fore.RED}You already though cube! Try another menu action.{Style.RESET_ALL}')

                # 2 - Продати бізнес
                elif choice == 2:
                    if p[1].facility_own_set:
                        p[1].sell_facility(input(f"{p[1].name}, choose own facility to sell: "))
                    else:
                        print(f"{Fore.RED}{p[1].name}, you don't have any own facility!{Style.RESET_ALL}")

                # 3 - Підвищити рівень бізнесу
                elif choice == 3:
                    if p[1].facility_own_set:
                        p[1].level_up_facility(input('Enter number own facility to level up: '))
                    else:
                        # print(f"{p[1].name}, you don't have any facility!")
                        print(f"{Fore.RED}{p[1].name}, you don't have any facility!{Style.RESET_ALL}")

                # 0 - Вийти (закінчити хід)
                elif choice == 0:
                    iteration_loop = False
                    print('\n', ' END ITERATION OF THIS PLAYER ', '\n\n\n\n', sep='='*14)
