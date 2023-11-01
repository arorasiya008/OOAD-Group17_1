from django.shortcuts import render,redirect
import json
from Auction.exceptions import InsufficientBalanceException,UserNotFoundException,InsufficientAmountException
from django.http import JsonResponse,HttpResponse
from Auction.models import Users,Payments,Items,Category,Bids
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from Auction.utils import SendNotif, SendConfirmationNotif, TimeBuffer, CheckBalance, CheckBid, AuctionInProgress 
from web3 import Web3
import os
import asyncio
from os.path import join, dirname
from dotenv import load_dotenv

contract_address = "0x6D892cD478BeE23f8dD91F10479b40bE9f4C9b7a"
abi = json.loads('[{"inputs":[{"internalType":"address","name":"_address","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"internalType":"address","name":"_from","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"checkWalletBalance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_to","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"makePayment","outputs":[],"stateMutability":"payable","type":"function"}]')
    
infura_url = ""
web3 = Web3(Web3.HTTPProvider(infura_url))

contract = web3.eth.contract(address = contract_address, abi = abi)

# Create your views here.

@login_required
async def makePayment(request,itemId):
    to_user_id = Items.objects.get(itemId = itemId).userId
    to_address = Users.objects.get(userId=to_user_id).walletAddress
    from_user_json=Bids.objects.get(itemId=itemId).contribution
    for userid, amount in from_user_json:
        from_address = Users.objects.get(userId = int(userid)).walletAddress
        await web3.eth.send_transaction({ 
            'to': to_address,
            'from': from_address,
            'value': amount,
        })
        payment = Payments(userId = int(userid), status = True,amount=amount,itemId=itemId)
        payment.save()
        print("deducted amount : ", amount)
        balance = web3.eth.get_balance(from_address)
        print("remaining balance : ", balance)

# add request handleers and send emails and map those view functionalities to the urls in the urls.py 

def home(request):
    return JsonResponse("hello")

def initiateAuction(request):
    if request.method == 'POST':
        user_id = request.session.get('userId')
        if not user_id:
            return JsonResponse({'error': 'User not authenticated.'}, status=401)
        item_data = {
            'itemName': request.POST.get('item_name'),
            'description': request.POST.get('item_description'),
            'itemImage': request.POST.get('item_image'),
            'startingBid': request.POST.get('starting_bid'),
            'auctionDuration': request.POST.get('auction_duration'),
            'categoryName': request.POST.get('category_name'),
            'auctionStartTime': timezone.now(),
            'userId' : user_id,
            # Add other fields as needed
        }

        try:
            item = Items.objects.create(**item_data)
            return JsonResponse({'success': 'Auction initiated successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

#assumption : itemId is present in url. If it is provided by frontend, change accordingly.
def eraseBid(request, itemId):
    if request.method == 'POST':
        bid_id = request.data.get('bidId')
        user_id = request.session.get('userId') #adjust key based on how session data is structured

        if not user_id:
            return JsonResponse({'error': 'User not authenticated.'}, status=401)

        if not TimeBuffer(itemId):
            return JsonResponse({'error': 'Cannot erase bid. Please try again in a few seconds.'}, status=400)

        if not AuctionInProgress(itemId):
            return JsonResponse({'error': 'Cannot erase bid. Auction has ended.'}, status=400)

        try:
            bid = Bids.objects.get(bidId=bid_id)
        except Bids.DoesNotExist:
            return JsonResponse({'error': 'Bid does not exist.'}, status=400)
            
        if user_id not in bid.contribution.keys():
            return JsonResponse({'error': 'You do not have permission to erase this bid.'}, status=403)

        bid.delete()
        return JsonResponse({'success': 'Bid erased successfully.'})

    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def placeBid(request, itemId):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_amounts = data.get('user_amounts', None)
            curr_user_id = request.session.get('userId')  # Adjust the key based on your session structure
            if not curr_user_id:
                return JsonResponse({'error': 'User not authenticated.'}, status=401)

            if user_amounts is None:
                return JsonResponse({'error': 'Invalid data. Missing user_amounts field.'}, status=400)

            if curr_user_id is None:
                return JsonResponse({'error': 'Current user ID not found in session.'}, status=400)

            if curr_user_id not in user_amounts: #if user placing the bid is not one of the bidders in contribution
                return JsonResponse({'error': 'Cannot place bid. You do not have permission to place this bid.'}, status=400)

            if not TimeBuffer(itemId):
                return JsonResponse({'error': 'Cannot place bid. Please try again in a few seconds.'}, status=400)
            
            if not AuctionInProgress(itemId):
                return JsonResponse({'error': 'Cannot place bid. Auction has ended.'}, status=400)

            try:
                item = Items.objects.get(id=itemId)
                bid = Bids.objects.create(itemId=itemId, contribution=user_amounts)
                try:
                    CheckBid(bid)
                    
                except UserNotFoundException as e:
                    error_message = str(e)
                    bid.delete()
                    return JsonResponse({'error': error_message}, status=400)

                except InsufficientBalanceException as e:
                    error_message = str(e)
                    bid.delete()
                    return JsonResponse({'error': error_message}, status=400)

                except InsufficientAmountException as e:
                    error_message = str(e)
                    bid.delete()
                    return JsonResponse({'error': error_message}, status=400)
                
                SendNotif(bid)
                SendConfirmationNotif(bid)
                
                for user_id in bid.contribution.keys():
                    if user_id not in item.bidders.all():
                        item.bidders.add(user_id)

                # Send relevant data to the frontend
                response_data = {
                    'success': 'Bid placed successfully.',
                    'item_id': itemId,
                    'bid_id': bid.bidId,
                    # Add other relevant data
                }

                return JsonResponse(response_data)

            except Items.DoesNotExist:
                return JsonResponse({'error': 'Item does not exist.'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def DisplayBids(request, itemId):
    try:
        user_id = request.session.get('userId')  # Adjust the key based on your session structure
        bids = Bids.objects.filter(userId=user_id, itemId=itemId)
        bid_data = [{'bidId': bid.bidId, 'itemId': bid.itemId, 'bidPlacedTime': bid.bidPlacedTime, 'amount': float(bid.amount)} for bid in bids]
        return JsonResponse({'bids': bid_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def DisplayAuctions(request, categoryName):
    try:
        items = Items.objects.filter(categoryName=categoryName)
        auctions_data = []
        for item in items:
            auction_data = {
                'itemId' : item.itemId,
                'itemName': item.itemName,
                'startingBid': item.startingBid,
                'imageURL': item.get_image_url(),  # Include the image URL
                # Add other fields as needed
            }
            auctions_data.append(auction_data)

        return JsonResponse({'auctions': auctions_data})
    
    except Items.DoesNotExist:
        return JsonResponse({'error': 'Category not found'}, status=404)

def DisplayCategory(request):
    categories = category.objects.all()
    categories_data=[]
    for category in categories :
        category_data = {
            'categoryId' : category.categoryId,
            'categoryName' : category.categoryName,
            'imageURL': category.get_image_url(),  # Include the image URL
            # Add other fields as needed
        }
        categories_data.append(category_data)
    return JsonResponse({'categories' : categories_data})
            

def Graph(request, itemId):
    try:
        item = Items.objects.get(id=itemId)
        
    except Items.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)
    try:
        bids = Bids.objects.filter(itemId=itemId)
        bid_ids = [bid.id for bid in bids]
        amounts = [bid.amount for bid in bids]
        data = {'bid_ids': bid_ids, 'amounts': amounts}
        return JsonResponse({'item': {'id': item.id, 'name': item.name}, 'graph_data': data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)})
        

def PieChart(request):
    userId = request.session.get('userId')  # Adjust the key based on your session structure
    if not userId:
        return JsonResponse({'error': 'User not authenticated.'}, status=401)
    try: 
        payments = Payments.objects.filter(userId=userId)
        num_categories = 5  # Update num_categories based on the number of actual categories
        category_sums = [0] * num_categories `
        category_names = [''] * num_categories
        for payment in payments:
            item = Items.objects.get(itemId=payment.itemId)
            category = Items.objects.get(categoryName=item.categoryName)
            category_sums[category.categoryId]+=payment.amount
            category_names[category.categoryId]=category.categoryName
        
        user_purchases = dict(zip(category_names, category_sums))
        return JsonResponse({'user_purchases': user_purchases})

    except Exception as e:
        return JsonResponse({'error': str(e)})


def get_user(request):
    user=request.session.get('userId')
    return JsonResponse({"user":user,"message":"success"})
