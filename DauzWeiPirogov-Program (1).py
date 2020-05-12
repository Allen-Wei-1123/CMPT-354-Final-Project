import psycopg2
from datetime import datetime

connection = None
cursor = None
username = 'postgres'
password = 'makulits2'
host = '127.0.0.1'
port = '5433'
database = 'postgres'

try:
# Connect to database
    connection = psycopg2.connect(user=username,
                                                                    password=password,
                                                                    host=host,
                                                                    port=port,
                                                                    database=database)

    cursor = connection.cursor()

# Print PostgreSQL Connection properties
    #print(connection.get_dsn_parameters())

 # Print PostgreSQL version
    #cursor.execute("SELECT version();")
    #record = cursor.fetchone()
    #print("The version of PostgreSQL", record)


# quick tutorial on how to print the outputs of queries if way she gave us isn't clear
    # thing = '*'
    #query = 'SELECT AVG(ABS(p.rewarded - p.requested)) FROM call c, proposal p WHERE c.id = p.callid and c.area = %s'
    #cursor.execute(query, ('VARIABLE TO USE FOR QUERY',))
    # rows = cursor.fetchall()
    # for row in rows:
    #     print (row)

# CLI starts here
# Assume all competitions in 2020
    task = None
    tasks = {'0', '1', '2', '3', '4', '5', '6', '7'}
    done = '0'

    #Loop over CLI/tasks, to exit change done to 1
    while(done == '0'):

        print()
        print('---What task would you like to perform?---')
        print('(1) Find all large competitions in a specified month')
        print('(2) Find a principle investigator in a specified area of large competitions')
        print('(3) Find the proposal(s) that request(s) the largest amount of money in a specified area')
        print('(4) Find the proposal(s) that are awarded the largest amount of money before a specified date ')
        print('(5) Find the average requested/awarded discrepancy of money from a specified area')
        print('(6) Assign a reviewer to a proposal')
        print('(7) Meeting and call scheduling by a specified room number and data')
        print('(0) Exit interface')
        print()

        task = input('Enter task number: ')
        while(task not in tasks):
            print('Invalid task number! Please try again.')
            task = input('Enter task number: ')

        #Exit
        if(task == '0'):
            break

        #Task 1
        if(task == '1'):
            rows = None
            print('You have chosen Task 1')
            month = input('Please enter a month, e.g. March: ')
            months = {'january': '01', 'february': '02', 'march': '03', 'april': '04', 'may': '05', 'june': '06', 'july': '07', 'august': '08', 'september': '09', 'october': '10', 'november': '11', 'december': '12'}
            month = month.lower()

            #Error checking for month
            while(month not in months):
                print('Invalid month, please try again')
                month = input('Please enter a month, e.g. March: ')
                month = month.lower()

            month = int(months[month])

            #Set up query checking for large proposals and print results
            query = " SELECT c.id, c.title FROM call c where c.status = 'open' and EXTRACT(MONTH from c.deadline) = %s and EXISTS(SELECT * FROM proposal p WHERE p.callid = c.id and p.status = 'submitted' and (p.requested > 20000 OR (10 < (SELECT COUNT(DISTINCT(coll.researcherid)) from collaborator coll WHERE coll.proposalid = p.id)))) "
            cursor.execute(query, [month])
            rows = cursor.fetchall()

            #Check if any results/output
            if(rows):
                #Formatting output
                print("\nResults: (format = call id, call title)")
                for row in rows:
                    print("    ", str(row)[1:-1])
                print("\n")
            else:
                print("No results to output.")
                print()
    


        #Task 2
        if(task == '2'):
            rows = None
            #ASSUME areas are Biology, Computer Science, Engineering for now
            areas = {'Biology', 'Computer Science', 'Engineering'}

            area = input('Specify an area you are interested in (e.g. Biology): ')
            area = area.title()
            while(area not in areas):
                print('Invalid area, please try again')
                area = input('Specify an area you are interested in (e.g. Biology): ')
                area = area.title()

            #User inputs researcher ID to see if they're a principle investigator for a proposal in specified area
            #Check if Researcher ID inputted is valid
            while(rows == None):
                try:
                    rid = int(input('Specify a researcher (by ID) you want to check: '))

                except ValueError:
                        print('Not an integer! Try again.')
                
                else:
                    query = " SELECT * FROM researcher WHERE id = %s "
                    cursor.execute(query, [rid])
                    rows = cursor.fetchone()

                    if(cursor.rowcount != 0):
                        break

                    else:
                        print('Invalid Researcher ID, please try again!')

            #Now that a valid area and researcher ID inputted, can start query
            query = " SELECT c.id, c.title FROM call c WHERE c.area = %s and EXISTS(SELECT * FROM proposal p WHERE p.status = 'submitted' and p.callid = c.id and p.pi = %s and (p.requested > 20000 OR (10 < (SELECT COUNT(DISTINCT(coll.researcherid)) FROM collaborator coll where coll.proposalid = p.id)))) "
            cursor.execute(query, (area, rid))
            rows = cursor.fetchall()

            #Check if any results/output
            if(rows):
                #Formatting output
                print("\nResults: (format = call id, call title)")
                for row in rows:
                    print("    ", str(row)[1:-1])
                print("\n")
            else:
                print("No results to output.")
                print()



        #Task 3
        if(task == '3'):
            rows = None
            #ASSUME areas are Biology, Computer Science, Engineering for now
            areas = {'Biology', 'Computer Science', 'Engineering'}

            area = input('Specify an area you are interested in (e.g. Biology): ')
            area = area.title()
            while(area not in areas):
                print('Invalid area, please try again')
                area = input('Specify an area you are interested in (e.g. Biology): ')
                area = area.title()

            query = " SELECT p.id FROM call c, proposal p WHERE c.id = p.callid and %s = c.area and p.requested = (SELECT MAX (p2.requested) FROM proposal p2, call c2 WHERE c2.id = p2.callid and c2.area = %s) "
            cursor.execute(query, (area, area))
            rows = cursor.fetchall()

            #Check if any results/output
            if(rows):
                #Formatting output
                print("\nResults: (format = proposal id)")
                for row in rows:
                    print("    ", str(row)[1:-2])
                print("\n")
            else:
                print("No results to output.")
                print()


        #Task 4
        if(task == '4'):
            rows = None
            #Check if input is in correct date format
            while(rows == None):
                date = input('Specify a date in the format YYYY-MM-DD: ')
                try:
                    dateTest = datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                        print('Not a correct date! Try again.')
                else:
                    query = " SELECT p.id FROM proposal p WHERE p.status = 'awarded' and p.submitdate < %s and  p.awarded = (SELECT MAX(p2.awarded) FROM proposal p2 WHERE p2.submitdate < %s and p2.status = 'awarded') "
                    cursor.execute(query, (date,date))
                    rows = cursor.fetchall()

                    #Check if any results/output
                    if(rows):
                        #Formatting output
                        print("\nResults: (format = proposal id)")
                        for row in rows:
                            print("    ", str(row)[1:-2])
                        print("\n")
                    else:
                        print("No results to output.")
                        print()
            

        #Task 5
        if(task == '5'):
            rows = None
            #ASSUME areas are Biology, Computer Science, Engineering for now
            areas = {'Biology', 'Computer Science', 'Engineering'}

            area = input('Specify an area you are interested in (e.g. Biology): ')
            area = area.title()
            while(area not in areas):
                print('Invalid area, please try again')
                area = input('Specify an area you are interested in (e.g. Biology): ')
                area = area.title()

            query = 'SELECT CAST(AVG(ABS(p.awarded - p.requested)) AS DECIMAL (14,2)) FROM call c, proposal p WHERE c.id = p.callid and c.area = %s'
            cursor.execute(query, (area,))
            rows = cursor.fetchall()

            #Check if any results/output
            if(rows):
                #Formatting output
                print("\nResults: (format = avg discrepancy)")
                for row in rows:
                    print("    ", str(row)[10:-4])
                print("\n")
            else:
                print("No results to output.")
                print()


        #Task 6
        if(task == '6'):
            atLeastOneAdded = False #Updated if new reviewers added
            
            rows = None
            #User inputs proposal ID
            #Check if Proposal ID ID inputted is valid
            while(rows == None):
                try:
                    pid = int(input('Specify a proposal (by ID) you want to check: '))

                except ValueError:
                        print('Not an integer! Try again.')
                
                else:
                    #Now that a valid proposal ID inputted, allow users to search which reviewers can be added to proposals without conflict
                    #Have to check proposal, collaborator and conflict tables to check for all potential conflicts
                    query= " SELECT r.id, r.firstname, r.lastname FROM researcher r WHERE r.id NOT IN (((SELECT c.researcher2 FROM (SELECT reviewerid AS existingreviewers FROM review WHERE proposal = %s) revs LEFT JOIN conflict c ON revs.existingreviewers = c.researcher1) UNION (SELECT reviewerid FROM review WHERE proposal = %s)) UNION (SELECT reviewcounts.id FROM (SELECT r2.id, COUNT(revs2.proposal) AS numreviews FROM researcher r2, review revs2 WHERE revs2.reviewerid = r2.id AND revs2.submitted = 'f' GROUP BY r2.id) reviewcounts WHERE reviewcounts.numreviews >= 3)) AND %s IN (SELECT id FROM proposal);"
                    cursor.execute(query, (pid,pid,pid))
                    rows = cursor.fetchall()

                    if(cursor.rowcount != 0):
                        #Formatting output
                        print("\nResults: (format = researcher id, first name, last name)")
                        for row in rows:
                            print("    ", str(row)[1:-1])
                        print("\n")

                        
                        #The user should not be able to specify which (if any) of these reviewers should be assigned to the specified proposal.
                        while(True):
                            pid2 = input('Specify a researcher (by ID) you want to assign as reviewer for proposal ' + str(pid) + ' \n(Type "q" to finish adding reviewers): ')
                            try:
                                pid2 = int(pid2)
                                
                            except ValueError:
                                if(pid2 == 'q' or pid2 == 'Q'):
                                    if(atLeastOneAdded):
                                        connection.commit()
                                        print('\n    Reviewer(s) successfully added!\n\n')
                                    break
                                else:
                                    print('Not an integer! Try again.')

                            else:
                                #Checks that inputted reviewer id is from the just-generated list.
                                atLeastOneAdded = True
                                acceptableInputsQuery= " SELECT r.id FROM researcher r WHERE r.id NOT IN (((SELECT c.researcher2 FROM (SELECT reviewerid AS existingreviewers FROM review WHERE proposal = %s) revs LEFT JOIN conflict c ON revs.existingreviewers = c.researcher1) UNION (SELECT reviewerid FROM review WHERE proposal = %s)) UNION (SELECT reviewcounts.id FROM (SELECT r2.id, COUNT(revs2.proposal) AS numreviews FROM researcher r2, review revs2 WHERE revs2.reviewerid = r2.id AND revs2.submitted = 'f' GROUP BY r2.id) reviewcounts WHERE reviewcounts.numreviews >= 3)) AND %s IN (SELECT id FROM proposal);"
                                cursor.execute(acceptableInputsQuery, (pid,pid,pid))
                                rows = cursor.fetchall()

                                isAcceptable = False
                                for row in rows:
                                    if str(pid2) == str(row)[1:-2]:
                                        isAcceptable = True

                                if(isAcceptable == False):
                                    print("This reviewer is not available (or doesn't exist)! Please try again.")
                                else:
                                    #Check if input is in correct date format
                                    while(True):
                                        date = input('Specify a review deadline in the format YYYY-MM-DD: ')
                                        try:
                                            dateTest = datetime.strptime(date, "%Y-%m-%d")
                                        except ValueError:
                                                print('Not a correct date! Try again.')
                                        else:
                                            query = "INSERT INTO review VALUES(DEFAULT,%s,%s,%s,'f');"
                                            cursor.execute(query, (pid,pid2,date))
                                            connection.commit()
                                            break
                        
                    else:
                        print('Invalid Proposal ID, please try again!')




        #Task 7
        if(task == '7'):
            rows = None
            #Check if a room is valid and available
            while(rows == None):
                try:
                    roomnum = int(input('Specify a room number to check availability: '))

                except ValueError:
                        print('Not an integer! Try again.')
                
                else:
                    query = " SELECT * FROM meeting WHERE roomnum = %s "
                    cursor.execute(query, [roomnum])
                    rows = cursor.fetchone()

                    if(cursor.rowcount != 0):
                        break

                    else:
                        print('Invalid Room Number, please try again!')

            #Now, user enters a date and program checks if room is available on that date

            #ASSUME for now user enters valid date format YYYY-MM-DD
            #Check if room is available at specific date
            while(cursor.rowcount != 0):
                date = input('Specify a data in the format YYYY-MM-DD: ')
                query = """ SELECT * FROM meeting WHERE roomnum = %s and date = %s """
                cursor.execute(query, (roomnum, date))

                rows = cursor.fetchone()
                if(cursor.rowcount != 0):
                    print('Room not available at that date, please try a new date!')

            #Now that room is available at date, user gets prompted to enter 3 competitions (calls) by ID 
            #Check for 3 valid calls
            print('Room is available at that date, now input 3 calls (by ID) to be discussed and decided on that day')
            calls = [-1, -1, -1]
            for i in range (0,3):
                rows = None
                while(rows == None):
                    try:
                        call = int(input('Specify call #' + str(i) + ': '))

                    except ValueError:
                            print('Not an integer! Try again.')
                
                    else:
                        query = """ SELECT * FROM call WHERE id = %s """
                        cursor.execute(query, [call])
                        rows = cursor.fetchone()

                        if(cursor.rowcount != 0):
                            calls[i] = call
                            break

                        else:
                            print('Invalid Call ID, please try again!')

            #Now that calls have been specified, can finally write query
            for i in range (0,3):
                call = calls[i]
                #CONTINUE FORM HERE
                query = """ SELECT COUNT(*) FROM proposal p, review r WHERE p.callid = %s and r.proposal = p.id and NOT EXISTS(SELECT * FROM meeting m, meetingreviewer mr WHERE mr.reviewerid = r.reviewerid AND m.date = %s and m.roomnum <> %s and mr.meetingid = m.id) """
            
                cursor.execute(query, (call, date, roomnum))
                rows = cursor.fetchall()

                #Check if any results/output
                if(rows[0][0] > 0):
                    print('Room ' + str(call) + ' is possible')
                else:
                    print('Room ' + str(call) + ' is impossible')


        
        
        #Ask user if they want to perform more tasks, 0 for yes, 1 for no
        done = input('Do you want to perform more tasks? Input 0 for yes, 1 for no: ')
        while(done not in ['0','1']):
            done = input('Invalid input! Please try again: ')





except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)

finally:
# close database connection.
    if (connection):
        cursor.close()
        connection.close()
        print("Exiting program. Goodbye!")
