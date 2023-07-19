import mysql.connector 
 
#Create the connection object  
myconn = mysql.connector.connect(host = "localhost", user = "root",passwd = "chinchaev007", database = "cars") 
 
#printing the connection object  
print(myconn)  
