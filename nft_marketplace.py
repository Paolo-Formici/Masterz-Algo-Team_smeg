import json
import pprint as pp
from src.blockchain_utils.credentials import get_client, get_account_credentials, get_indexer, add_account_to_config, \
    fund_account
from src.services.nft_service import NFTService
from src.services.nft_marketplace import NFTMarketplace

UNIT_NAME = "FAB30"
ASSET_NAME = "RLI5@01"
NFT_URL = "nft_metadata/FAB30RLI5@01_meta.json"
ASA_VALID_BUYER_TKN = 501
BUYER_TKN = 501
FUND = False


# ------------------------------------------------------------------------------------------ #
# ------------------------------# CREATE CLIENT AND ACCOUNTS #------------------------------ #
# ------------------------------------------------------------------------------------------ #

print("1. Creating accounts credentials and adding them to configuration file...")
# generate 3 accounts, company, buyer_01, buyer_02
add_account_to_config()
add_account_to_config()
add_account_to_config()


print("\n--------------------------------------------")
print("2. Creating client to interact with the network...")
client = get_client()

# print("Client status:")
# pp.pprint(client.status())

print("\n--------------------------------------------")
print("3. Get accounts credentials and indexer...\n")
company_pk, company_address, _ = get_account_credentials(account_id=1)
buyer_01_pk, buyer_01_address, _ = get_account_credentials(account_id=2)

indexer = get_indexer()

print("Company credentials:\n- Address: {}\n- Private key: {}".format(company_address, company_pk))
print("Buyer_01 credentials:\n- Address: {}\n- Private key: {}".format(buyer_01_pk, buyer_01_address))
print("Buyer_02 credentials:\n- Address: {}\n- Private key: {}".format(buyer_02_pk, buyer_02_address))

if FUND:
    print("\n--------------------------------------------")
    print("3a. Fund accounts...")
    fund_account(client, company_address)
    fund_account(client, buyer_01_address)
else:
    print("\nCheck account balances...")
    print("Company:\n- address: {}\n- balance:{} microAlgos".format(
        client.account_info(address=company_address).get("address"),
        client.account_info(address=company_address).get("amount")
    ))
    print("Buyer_01:\n- address: {}\n- balance:{} microAlgos".format(
        client.account_info(address=buyer_01_address).get("address"),
        client.account_info(address=buyer_01_address).get("amount")
    ))

# -------------------------------------------------------------------------- #
# ------------------------------# CREATE NFT #------------------------------ #
# -------------------------------------------------------------------------- #

print("\n--------------------------------------------")
print("4. Creating NFT...")
nft_service = NFTService(nft_creator_pk=company_pk,
                         nft_creator_address=company_address,
                         client=client,
                         unit_name=UNIT_NAME,
                         asset_name=ASSET_NAME,
                         nft_url=NFT_URL)

tx_id = nft_service.create_nft()

print("\n--------------------------------------------")
print("4a. Created NFT checks:")

print("- NFT id: {}".format(nft_service.nft_id))
print("- NFT Holder address: {}".format(
    indexer.accounts(asset_id=nft_service.nft_id).get("accounts")[0].get("address")))

print("- NFT asset info:")
pp.pprint(indexer.asset_info(asset_id=nft_service.nft_id))

# ---------------------------------------------------------------------------------- #
# ------------------------------# CREATE MARKETPLACE #------------------------------ #
# ---------------------------------------------------------------------------------- #

print("\n--------------------------------------------")
print("5. Creating the application to interact with clients who bought the product...")
nft_marketplace = NFTMarketplace(admin_pk=company_pk,
                                 admin_address=company_address,
                                 nft_id=nft_service.nft_id,
                                 asa_valid_buyer_tkn=ASA_VALID_BUYER_TKN,
                                 client=client)

tx_id = nft_marketplace.app_initialization(nft_owner_address=company_address)

print("Application parameters:\n",
      "- Admin address: {}\n- Admin private key: {}\n- App id: {}\n- NFT id: {}\n- Valid buyer tkn: {}".format(
          nft_marketplace.admin_address,
          nft_marketplace.admin_pk,
          nft_marketplace.app_id,
          nft_marketplace.nft_id,
          nft_marketplace.asa_valid_buyer_tkn
      ))

print("\n- Application info:")
pp.pprint(indexer.applications(application_id=nft_marketplace.app_id))


# -------------------------------------------------------------------------- #
# ------------------------------# SET ESCROW #------------------------------ #
# -------------------------------------------------------------------------- #

print("\n--------------------------------------------")
print("6. Change NFT credentials to grant escrow address transfer grants...")
tx_id = nft_service.change_nft_credentials_txn(escrow_address=nft_marketplace.escrow_address)

print("- NFT updated asset info:")
pp.pprint(indexer.asset_info(asset_id=nft_service.nft_id))

print("\n--------------------------------------------")
print("7. Initialize escrow...")
tx_id = nft_marketplace.initialize_escrow()

print("\n--------------------------------------------")
print("8. Fund escrow...")
tx_id = nft_marketplace.fund_escrow()


# ---------------------------------------------------------------------------------------------- #
# ------------------------------# MAKE NFT AVAILABLE TO TRANSFER #------------------------------ #
# ---------------------------------------------------------------------------------------------- #

print("\n--------------------------------------------")
print("9. Company registers product sale and enables the NFT to be received by the buyer...")
tx_id = nft_marketplace.make_sell_offer(nft_owner_pk=company_pk)


print("\n- Updated application info:")
pp.pprint(indexer.applications(application_id=nft_marketplace.app_id))


# ------------------------------------------------------------------------------------- #
# ------------------------------# TRANSFER NFT TO BUYER #------------------------------ #
# ------------------------------------------------------------------------------------- #

print("\n--------------------------------------------")
print("10. The buyer signs in on the company application and creates an account")
print("The buyer scans the qr code and receives the following token: {}".format(BUYER_TKN))
print("The scan triggers the following operations...")

print("The buyer sends opt in transaction to allow receiving the asset from the company(owner)")
tx_id = nft_service.opt_in(buyer_01_pk)

print("The buyer sends an application call to receive the nft with the received token: {}")
tx_id = nft_marketplace.buy_nft(nft_owner_address=company_address, buyer_address=buyer_01_address,
                                buyer_pk=buyer_01_pk, buyer_tkn=BUYER_TKN)


print("\n- Updated application info:")
pp.pprint(indexer.applications(application_id=nft_marketplace.app_id))

print("\n- Buyer account info:")
pp.pprint(indexer.accounts(asset_id=nft_marketplace.nft_id))

print("- NFT updated asset info:")
pp.pprint(indexer.asset_info(asset_id=nft_service.nft_id))


# ------------------------------------------------------------------------------------------------- #
# ------------------------------# UPDATE AND CHECK WARRANTY-REPAIRS #------------------------------ #
# ------------------------------------------------------------------------------------------------- #

print("\n--------------------------------------------")
print("11. Here we do checks on the warranty of the product and we also simulate a reparation")
print("Each repair is stored inside the nft metadata as well as all warranty details about the product")

print("\n Current metadata:")
with open('nft_metadata/FAB30RLI5@01_meta.json', 'r') as f:
    data = json.load(f)
pp.pprint(data)

print("\n Warranty checks for a specific date:")
nft_marketplace.check_product_warranty()

print("\n Simulating a repair and updating the metadata")
nft_marketplace.update_nft_metadata(
    repair_date="2022-03-01T00:00:00Z",
    repair_description="Fixed a leak in the water dispenser",
    technician="Jane Doe"
)

print("\n Updated metadata:")
with open('nft_metadata/FAB30RLI5@01_meta.json', 'r') as f:
    data = json.load(f)
pp.pprint(data)

print("\n -------------- Demo finished! --------------")
