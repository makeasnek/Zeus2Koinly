import os,csv
def sats_to_BTC(sats:int)->float:
    btc=sats/100000000
    return btc
def float_to_str(inputfloat:float)->str:
    return '{:.8f}'.format(inputfloat)

if __name__=="__main__":
    print("Zeus exports three different CSV files, we will ask for the location of each one if it cannot be found")
    print("Please type in the full path if prompted")
    print("WINDOWS users: You must escape slashes so C:\folder\file.txt should be entered at C:\\folder\\file.txt")
    print("If you want to skip importing a file, just leave your answer blank (hit enter)")

    # check if csv import files already exist, prompt if they don't
    if os.path.exists('invoices.csv'):
        invoices_path=os.path.join(os.getcwd(),'invoices.csv')
    else:
        invoices_path=input("invoices.csv=")
    if os.path.exists('payments.csv'):
        payments_path=os.path.join(os.getcwd(),'payments.csv')
    else:
        payments_path=input("payments.csv=")
    if os.path.exists('onchain.csv'):
        onchain_path=os.path.join(os.getcwd(),'onchain.csv')
    else:
        onchain_path=input("onchain.csv=")
    known_paths={
        'INVOICES':invoices_path,
        'PAYMENTS':payments_path,
        'ONCHAIN':onchain_path
        }
    # verify all given files exist
    for known_path in known_paths.values():
        if known_path=="":
            continue
        if not os.path.exists(known_path):
            print("Error, path {} doesn't exist! Try running the script again.".format(known_path))
            quit()
    
    final_csv=[] # final list which will be written to the output.csv file
    # a list of keys which can be converted gracefully from import file to output file
    convert_keys={
        'Amount Paid (sat)':'Received Amount',
        'Payment Hash':'TxHash',
        'Transaction Hash':'TxHash',
        'Creation Date':'Date',
        'Timestamp':'Date',
    }
    # ignore these keys
    ignore_keys={'Expiry','Payment Request'} # skip
    # a list of all keys which will be exported. More is added to this later
    export_keys={'Description','Received Currency','Sent Currency'}
    # keys which should be concatenated into the notes field
    notes_keys={'Memo','Note','Destination'}

    # for each CSV file
    for csv_type,known_path in known_paths.items():
        with open(known_path, mode ='r') as file:    
            csvFile = csv.DictReader(file)
            # read in CSV file line by line
            for line in csvFile:
                notes_field='' # start with a blank notes field
                new_line={} # we put output data into here
                for key,value in line.items():
                    write_value=value
                    write_key=key
                    if key in ignore_keys:
                        continue
                    elif key in notes_keys:
                        # special handling for "notes" fields
                        if value.strip()!='':
                            notes_add='{}:{} + '.format(key,value)
                            notes_field=notes_field+notes_add
                        continue
                    elif key in {'Amount Paid (sat)'} and csv_type=='INVOICES':
                        # special handling for this field, koinly wants BTC not SATs
                        converted=sats_to_BTC(int(value))
                        write_value=float_to_str(converted)
                        write_key='Received Amount'
                        new_line['Received Currency']='BTC'
                    elif key in {'Amount Paid (sat)'} and csv_type=='PAYMENTS':
                        # special handling for this field, koinly wants BTC not SATs
                        converted=sats_to_BTC(int(value))
                        write_value=float_to_str(converted)
                        write_key='Sent Amount'
                        new_line['Sent Currency']='BTC'
                    elif key=='Amount (sat)':
                        # special handling for this field, figure out if tx is inbound or outbound
                        numbered=int(value)
                        if numbered>0:
                            write_key='Received Amount'
                            new_line['Received Currency']='BTC'
                        elif numbered<0:
                            write_key='Sent Amount'
                            new_line['Sent Currency']='BTC'
                        elif numbered==0:
                            continue
                        converted=abs(sats_to_BTC(numbered))
                        write_value=float_to_str(converted)
                    elif key=='Total Fees (sat)':
                        # special handling for this field, koinly wants BTC not SATs
                        numbered=int(value)
                        if numbered>0: # outgoing payment, you paid a fee
                            converted=abs(sats_to_BTC(numbered))
                            write_value=float_to_str(converted)
                            write_key='Fee Amount'
                    elif key not in convert_keys:
                        print("Error: found unknown key {}, exported CSV may not be complete!".format(key))
                        continue
                    else:
                        write_key=convert_keys[key]
                    if write_key not in export_keys:
                        export_keys.add(write_key)
                    new_line[write_key]=write_value 
                new_line['Description']=notes_field
                final_csv.append(new_line)
    # write output csv
    with open('output.csv','w') as my_file:
        dict_writer = csv.DictWriter(my_file, export_keys)
        dict_writer.writeheader()
        for transaction in final_csv:
            dict_writer.writerow(transaction)
    print('Script complete! Check output.csv for your results')
    print('If you found this script useful, please consider donating a few sats to me as a thank you')
    print('makeasnek@zeuspay.com')
    print('bc1q4zqhmyp8yw4zehw2tf4sjvqc5dv9dm747ssh0p')

        
          
    
        
                        
