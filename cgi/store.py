#!/usr/bin/python
import os,cgi, cgitb

cgitb.enable()  # for troubleshooting

#the cgi library gets vars from html
data = cgi.FieldStorage()
filename = data['filename'].value
contenido = data['contenido'].value

if filename:
   open('/../config/' + filename, 'wb' ).write( contenido )