# ERC721 token ownership tracker

## Description
The Nft tracker fetches the Nft ownership by analyzing all events occurred from ERC721 contracts of the Ehtereum mainnet, and keeps in the Neo4j db. 
It will be going to fetch the event from latest block every once in a minute.

## Environment Setup

### Install Python 3.x.

### Install dependencies package
``` bash
pip install -r requirements.txt
```

### Database connection setting

``` code
driver = GraphDatabase.driver('***connection uri***', auth=basic_auth('***user***', '***password***'))
```

## Database Schema
(:NftCollection { address: '0x...' })-[:PartOf]->(:Nft { id: '0x...' })<-[:Owned { since: <timestamp> }]-(:EtherAddress { address: '0x...' })

### Description about properties of the Node and Relation
* NftCollection
    - address : contract address
* Nft
    - id : nft id
* EtherAddress
    - address : nft owner's address
* Owned
    - since : owned time

## Fixed issues
* Nft is linked to only one collection. In a word, a Nft can't be linked on several collections.
If Nft linked to any collection exists already on the db, tracker will create new Nft node and make new relationship with other collection. 
Currently, this issue has been fixed.
