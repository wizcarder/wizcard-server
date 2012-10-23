#!/bin/sh

# Change the parameters here for another DB
USER=root
PWD=''
DB=test

# Create some test data
mysql -u$USER -p$PWD -D$DB 

        "userID":       "thewizkid",                                                      
        "first":        "anand",                                                          
        "last":         "ammundi",                                                        
        "company":      "wiz inc.",                                                       
        "title":        "founder",                                                        
        "phone":        "(408)-xxx-yyyy",                                                 
        "email":        "thewizkid@whiz.selfip.com",                                      
        "street":       "dunholme ave",                                                   
        "city":         "sunnyvale",                                                      
        "state":        "california",                                                     
        "zip":          "94087",                                                          
        "location":     [{"lat":37.32300, "lng":-122.03218}]                              
        }                           
