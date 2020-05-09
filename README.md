# haukiposti

A custom masspost & invoice creation program made with Python. Originally made for a non-profit organization.
Includes UI made with PySimpleGUI, invoice & stickerheet functions made with the open-source ReportLab PDF & PubCode libraries. Email sending & authentication is made via Gmail API with Google Authentication libraries.

*Currently UI & manual (in assets folder) is ONLY IN Finnish. Source code is mostly English.*

*Requires Gmail API credentials to work!*

This program allows you to send CC emails to multiple people at once, and personalized invoices as an attachment.
Messages can be stylized with custom markdown implementation.

Invoices are created based on the standardized Finnish bank transfer form and the program creates a random reference number and dynamically puts the price on the form based on the receivers member type of the non-profit.

Required libraries to run:
PySimpleGUI,
ReportLab PDF library,
Pillow/PIL,
PubCode,
Google API Client, google-auth-httplib2, google-auth-oauthlib

*May also need PyInstaller to be installed*
