#!/usr/bin/env python3

import re

from scapy.all import *

'''
Balckjack game rule

Blackjack hands are scored by their point total. The hand with the highest total wins as long as it doesn't exceed 21; a hand with a higher total than 21 is said to bust. Cards 2 through 10 are worth their face value, and face cards (jack, queen, king) are also worth 10. An ace's value is 11 unless this would cause the player to bust, in which case it is worth 1. A hand in which an ace's value is counted as 11 is called a soft hand, because it cannot be busted if the player draws another card.

The goal of each player is to beat the dealer by having the higher, unbusted hand. Note that if the player busts he loses, even if the dealer also busts (therefore Blackjack favors the dealer). If both the player and the dealer have the same point value, it is called a "push", and neither player nor dealer wins the hand. Each player has an independent game with the dealer, so it is possible for the dealer to lose to one player, but still beat the other players in the same round.

After initial bets are placed, the dealer deals the cards, either from one or two hand-held decks of cards, known as a "pitch" game, or more commonly from a shoe containing four or more decks. The dealer gives two cards to each player, including himself. One of the dealer's two cards is face-up so all the players can see it, and the other is face down. (The face-down card is known as the "hole card". In European blackjack, the hole card is not actually dealt until the players all play their hands.) The cards are dealt face up from a shoe, or face down if it is a pitch game.

In this programme, the Raspberry Pi will be the dealer, and you(lab machine) will be the player.

'''

class Black(Packet):
    name = "Black"
    fields_desc = [ StrFixedLenField("P", "P", length=1),
                    StrFixedLenField("Four", "4", length=1),
                    XByteField("version", 0x01),
                    StrFixedLenField("op", "+", length=1),
    				IntField("hand", 0),
                    IntField("ace", 0),
                    IntField("result", 11)]
                    
bind_layers(Ether, Black, type=0x1234)

import random

#Initial the global variables
#A playing card has four suits in total, and each of them has 13 different ranks
#In blackjack, each rank has the same value as its rank except from J, Q, K and A, which has a value of 10, 10, 10, 10, and 11(or 1, but this case will be discussed later) respectively

suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}


#Define a calss of card which allows quick return of the card value
class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank} of {self.suit}"

#creat a random deck for the game
#the shuffle function make the deck random
#the deal funciton then randomly pick a card for the user or dealer
class Deck:
    def __init__(self):
        self.deck = []
        for suit in suits:
            for rank in ranks:
                self.deck.append(Card(suit, rank))

    def shuffle(self):
        random.shuffle(self.deck)

    def deal(self):
        return self.deck.pop()
        
#The class is used to represent the cards on your hand
#The add_card function add a card to your hand card, and it also sums up the value of your card
#The adjust_for_ace function is used to adjust the value of ace to 1 when the total value exceeds 21
class Hand:
    def __init__(self):
        self.cards = []
        self.value = 0
        self.aces = 0

    def add_card(self, card):
        self.cards.append(card)
        self.value += values[card.rank]
        if card.rank == 'A':
            self.aces += 1

    def adjust_for_ace(self):
        while self.value > 21 and self.aces:
            self.value -= 10
            self.aces -= 1
            
    def clear(self):
    	self.cards.clear()
    	self.value = 0
    	self.aces = 0

#The chip calss represents the chips you have
#Win_bet represents the case where you win the game and therefore your chip increase
#Lose-bet represents the case where you lose the game and therefore your chip decrease
#The amount of chip you increase and decrease depends on the bet you made before the game start
class Chips:
    def __init__(self):
        self.total = 100
        self.bet = 0

    def win_bet(self):
        self.total += self.bet

    def lose_bet(self):
        self.total -= self.bet

#This is the function for making a bet
def take_bet(chips):
    while True:
        try:
            chips.bet = int(input("Enter your bet amount: "))
            
            #If your chip balance is lower than the bet you made, the system will notify theplayer
            
            if chips.bet > chips.total:
                print("Insufficient chips!")
            else:
                break
                
            #If the player input a non-integer value, the system will ask the player to enter again     
        except ValueError:
            print("Invalid input. Please enter an integer.")


#This is a function for adding a card
def hit(deck, hand):
    hand.add_card(deck.deal())
    hand.adjust_for_ace()

#This is a function for asking the player if they want to take another card or stop
def hit_or_stand(deck, hand):
    global playing
    while True:
        #Ask the user if they want more card
        choice = input("Do you want to hit or stand? (h/s): ")
        #h stands for hit means more card, then action hit
        if choice.lower() == 'h':
            hit(deck, hand)
        #s stands for stand means stop and no more card needed
        elif choice.lower() == 's':
            print("Player stands. Dealer's turn.")
            playing = False
        #If the input is not what we are expecting, return error message
        else:
            print("Invalid input. Please enter 'h' or 's'.")
            continue
        break

#This function is used to display the players' and the dealers' card 
def show_some(player, dealer):
    print("\nPlayer's cards:")
    for card in player.cards:
        print(card)
    #The dealer has one hidden card that is not going to display
    print("\nDealer's cards:")
    print("Hidden Card")
    for card in dealer.cards[1:]:
        print(card)

#This function is used to show all player's hand cards and dealer's hand cards.
#This is usually used at the end of the game
def show_all(player, dealer):
    print("\nPlayer's cards:")
    for card in player.cards:
        print(card)
    print(f"Player's hand value: {player.value}")
    print("\nDealer's cards:")
    for card in dealer.cards:
        print(card)
    print(f"Dealer's hand value: {dealer.value}")

#This function is for the case where player bust and lose chips
def player_busts(player, chips):
    print("Player busts!")
    chips.lose_bet()

#This function is for the case where player wins and wins chips
def player_wins(player, dealer, chips):
    print("Player wins!")
    chips.win_bet()

#This function is for the case where dealer bust and win chips
def dealer_busts(player, dealer, chips):
    print("Dealer busts! Player wins!")
    chips.win_bet()

#This function is for the case where player wins and lose chips
def dealer_wins(player, dealer, chips):
    print("Dealer wins!")
    chips.lose_bet()

#This is when the player and the dealer have blackjack(21points), then they enter a push round
def push(player, dealer):
    print("It's a tie! Push.")
    
#This is the funciton for sending the packet to Raspberry Pi
def send_hand(value,ace=0):
    dst_mac = "00:00:00:00:00:01"
    src_mac= "00:00:00:00:00:02"
    src_ip = "169.254.21.80"
    dst_ip = "192.168.10.2"
    iface = "enx0c37965f8a0a"
    c = 0
    pkt = Ether(dst='00:04:00:00:00:00', type=0x1234) / Black(op='+', hand=int(value), ace=int(ace))
    
    pkt = pkt/' '
    resp = srp1(pkt, iface=iface,timeout=5, verbose=True)
    
    if resp:        		
        var = resp[Black]
        if var:
             res = var.result		
             return res 
        else:
            return 'error'
            print("cannot find Black header in the packet")
    else:	
        print("Didn't receive response")
        return 'error'
    #    except Exception as error:
    #    	print('00', error)
            
        

# Initialize the game
#Set up the deck
#set up initial hand cards
#set up initial chips
deck = Deck()
deck.shuffle()
player_hand = Hand()
dealer_hand = Hand()
player_chips = Chips()

#Main Game body itself
while True:
    # Opening message
    print("Welcome to Blackjack!")
    player_hand.clear()
    dealer_hand.clear()

    # Take player's bet
    take_bet(player_chips)

    # Deal two cards to the player and dealer
    #Initially two cards will be allocated to the dealer and the player
    player_hand.add_card(deck.deal()) #pop a card from the deck and add to hand card
    dealer_hand.add_card(deck.deal())
    player_hand.add_card(deck.deal())
    dealer_hand.add_card(deck.deal())
    

    # Show initial cards (hide one of the dealer's cards)
    show_some(player_hand, dealer_hand)

    #Define the game ending variables
    playing = True

    # Player's turn
    while playing:
        #Ask the player if they want to hit or stand
        hit_or_stand(deck, player_hand)
        #show hand cards
        show_some(player_hand, dealer_hand)
        #Check if the player bust or not
        if player_hand.value > 21:
            player_busts(player_hand, player_chips)
            show_all(player_hand,dealer_hand)
            break

    #If the player hasn't bust yet, the dealer will then continue to play
        if player_hand.value <= 21:
        # Dealer's turn (automated with Raspberry Pi switch)
        #while dealer_hand.value < 17:
            #hit(deck, dealer_hand)
        	res = send_hand(dealer_hand.value,dealer_hand.aces)
        	print('pkt', res)
        	if res == 1:
        		hit(deck,dealer_hand)                   
            
            
        # The above code is for original python ongly version game, but now we want to send the packets to Raspberry Pi and let it to make the desicion

        # Show all cards
        show_all(player_hand, dealer_hand)

        # Winning conditions
        if dealer_hand.value > 21:
            dealer_busts(player_hand, dealer_hand, player_chips)
        elif dealer_hand.value > player_hand.value:
            dealer_wins(player_hand, dealer_hand, player_chips)
        elif dealer_hand.value < player_hand.value:
            player_wins(player_hand, dealer_hand, player_chips)
        else:
            push(player_hand, dealer_hand)

    # Player's chips total
    print(f"\nPlayer's total chips: {player_chips.total}")

    # Ask to play again
    play_again = input("Do you want to play again? (y/n): ")
    if play_again.lower() != 'y':
    	break
    	

