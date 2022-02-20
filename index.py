import sys
from web3 import Web3
from neo4j import (
    GraphDatabase,
    basic_auth,
)
import time

w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/0f9fab07058c4d90afd7b3f6014d491f'))
#w3 = Web3('http://172.30.77.160:8546')
#w3 = Web3(Web3.WebSocketProvider('ws://172.30.77.160:8546'))

driver = GraphDatabase.driver('bolt://localhost:7687', auth=basic_auth('neo4j', 'qwer1234'))
#driver = GraphDatabase.driver('bolt://172.30.77.160:7687', auth=basic_auth('Chris', 'ChrisMeta67%!'))

def get_db():
    neo4j_db = driver.session(database='nft')
    #neo4j_db = driver.session()
    return neo4j_db 

event_signature_hash = w3.sha3(text='Transfer(address,address,uint256)').hex()
print('EVENT SIGNATURE HASH: ', event_signature_hash)

def create_nft_ownership(data):    
    db = get_db()

    query = ('MATCH (n:Nft {id: $nft_id})<-[:PartOf]-(nc:NftCollection) '
            'WHERE nc.address <> $contract_address '
            'RETURN n'
        )
    ret = db.run(query, data).single()
    type = 1
    
    if (ret is None):
        type = 1
    else:
        type = 2

    print('TYPE: ', type)

    def _create_and_return_nft_ownership(tx, data, type):
        if (type == 1):
            query = ('MERGE (nc:NftCollection {address:$contract_address}) '
                'MERGE (n:Nft {id: $nft_id}) '
                'MERGE (ea:EthAddress {address: $to}) '
                'MERGE (n)<-[:PartOf]-(nc) '
                'MERGE (ea)-[r:Owned {since: $timestamp}]->(n) '
                'RETURN ea.address as owner, r.since as time, n.id as nft_id, nc.address as contract_address'
            )
            return tx.run(query, data)
        else:
            query = ('MERGE (nc:NftCollection {address:$contract_address}) '
                'MERGE (ea:EthAddress {address: $to}) '    
                'MERGE (nc)-[:PartOf]->(n:Nft {id: $nft_id}) '        
                'MERGE (ea)-[r:Owned {since: $timestamp}]->(n) '
                'RETURN ea.address as owner, r.since as time, n.id as nft_id, nc.address as contract_address'
            )
            return tx.run(query, data)


    ret = db.write_transaction(_create_and_return_nft_ownership, data, type)
    
    db.close()

def main():
    block_number = 0
    with open('./lt_block.dt', 'r') as f:
        block_number = int(f.read())

    print('last block number: ', block_number)

    while True:
        #{'fromBlock': 'latest', 'topics': [event_signature_hash]}
        try:
            if block_number == 0:
                filt = w3.eth.filter({'fromBlock': 'latest', 'topics': [event_signature_hash]})
            else:
                filt = w3.eth.filter({'fromBlock': block_number + 1, 'topics': [event_signature_hash]})

            logs = w3.eth.get_filter_changes(filt.filter_id)
            for log in logs:
                topics = log['topics']
                if (len(topics) < 4):
                    continue
                
                address = log['address']
                block_number = log['blockNumber']
                #event_hash = topics[0].hex() 
                from_ = topics[1].hex() 
                to = topics[2].hex()
                nft_id = topics[3].hex()

                if (int(from_, 0) == 0):
                #    from = to to = contract address
                    print('<<<<<<<<<<<<<<<<< MINT >>>>>>>>>>>>>>>>>')
                #    print(log)
                #    from_ = to
                #    to = address
                #    continue

                if (int(to, 0) == 0):
                #   from = from to = contract address
                    print('<<<<<<<<<<<<<<<<< Upgrade Comic, Fuse Tokens>>>>>>>>>>>>>>>>>')
                #   print(log)
                #   to = address
                #   continue
                    
                print('constract address: ', address, 'from: ', from_, 'to: ', to, 'nft id: ', nft_id)
                #print(log)
                #return
                data = {
                    'contract_address': address, 'from': from_, 'to': to, 'nft_id': nft_id, 'timestamp': time.time()
                }

                create_nft_ownership(data)
        except Exception:
            print('error')
            print(sys.exc_info())
        finally:
            ret = w3.eth.uninstall_filter(filt.filter_id)
            print('uinstall status: ', ret)

        with open('./lt_block.dt', 'w') as f:
            f.write('%d' % block_number)

        time.sleep(1)
    
    
if __name__ == '__main__':
    main()