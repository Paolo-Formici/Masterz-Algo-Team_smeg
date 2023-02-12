# Masterz-Algo-Team_smeg
Algorand project for Masterz

This project is a demo of an NFT marketplace for a company that sells home appliances.
It simulates the behaviour of a marketplace where users which buy the phisycal product receive the corresponding NFT that represent it.
Each NFT has a metadata field that keeps track of warranty state, owners and details about the product itself.

The logic is built using a stateful smart contract for the application and a stateless smart contract for the escrow.
The buyer scans the qr code that comes with the product throught the company application and, after the token sent gets validated, receives the NFT inside is wallet.
Lastly some check over the NFT metadata show how easy it is to get all detailed info about the product from the moment it being built to the end of it lifecycle and over.
