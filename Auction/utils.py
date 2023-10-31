from django.core.mail import send_mail
from django.utils import timezone
from Auction.models import Bids, Items, Users
from web3 import Web3
from Auction.exceptions import UserNotFoundException, InsufficientBalanceException, InsufficientAmountException


def SendNotif(bid):
    item = Items.objects.get(itemId=bid.itemId)
    curr_bidders = list(bid.contribution.keys())
    req_bidders = [bidder for bidder in item.bidders if bidder not in curr_bidders]
    for bidder in req_bidders:
        user = Users.objects.get(userId=bidder)

        subject = 'New Bid Placed on {}'.format(item.itemName)
        message = 'Hello {},\n\nA new bid has been placed on the item "{}".\n\nSincerely,\nYourApp Team'.format(
            user.username, item.itemName
        )
        from_email = 'yourapp@example.com' #add our email id here
        recipient_list = [user.email]

        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

def SendConfirmationNotif(bid):
    item = Items.objects.get(itemId=bid.itemId)
    curr_bidders = list(bid.contribution.keys())

    for bidder in curr_bidders:
        user = Users.objects.get(userId=bidder)

        subject = 'New Bid Successfully Placed on {}'.format(item.itemName)
        message = 'Hello {},\n\nYou have successfully placed a new bid on the item "{}".\n\nSincerely,\nYourApp Team'.format(
            user.username, item.itemName
        )
        from_email = 'yourapp@example.com' #add our email id here
        recipient_list = [user.email]

        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

def TimeBuffer(itemId):
    item = Items.objects.get(itemId=itemId)

    if timezone.now()< item.timeBuffer:
        return False
    else:
        item.timeBuffer = timezone.now() + timezone.timedelta(milliseconds=1000)
        item.save()
        return True
    
def CheckBalance(userId, bidAmount):
    w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))  #add url for our ethereum node here

    user = Users.objects.get(userId=userId)
    wallet_address = user.walletAddress

    try:
        balance_wei = w3.eth.get_balance(wallet_address)
        balance_eth = w3.fromWei(balance_wei, 'ether')
        
        if balance_eth >= bidAmount:
            return True
        else:
            return False

    except Exception as e:
        return False

def MaxBid(itemId):
    bids_list = Bids.objects.filter(itemId=itemId)
    max_bid = max(bids_list, key=lambda x: x.amount)
    return max_bid

def CheckBid(bid):
    total_amount = sum(bid.contribution.values())
    max_bid = MaxBid(bid.itemId).amount
    bid.amount = total_amount
    bid.save()

    for userId, amount in bid.contribution.items():
        try:
            user = Users.objects.get(userId=userId)
        except Users.DoesNotExist:
            raise UserNotFoundException(f"Error: Cannot place bid. User {userId} does not exist.")

        if not CheckBalance(userId, amount):
            raise InsufficentBalanceException(f"Error: Cannot place bid. User {userId} has insufficient balance.")
        
    if total_amount <= max_bid:
        raise InsufficentAmountException(f"Error: Cannot place bid. The bid amount is insufficient.")
        
    return True

def AuctionInProgress(itemId):
    item = Items.objects.get(itemId=itemId)
    if item.auctionStartTime <= timezone.now() < item.auctionStartTime + item.auctionDuration:
        return True
    else:
        return False




    
    






    


