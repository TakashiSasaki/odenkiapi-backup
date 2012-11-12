from __future__ import unicode_literals, print_function
import logging
from model.Sender import Sender
from MyRequestHandler import MyRequestHandler

class SenderRequestHandler(MyRequestHandler):
    
    def get(self):
        gql = Sender.gql("ORDER BY senderId DESC")
        #senders = Sender.all()
        senders = gql.run()
        template_values = {}
        template_values["senders"] = []
        for sender in senders:
            template_values["senders"].append(
                                           {"senderId": sender.senderId,
                                            "protocol":sender.protocol,
                                            "ipAddress": sender.ipAddress,
                                            "port":sender.port})
            logging.info(template_values)
        self.writeWithTemplate(template_values, "Sender")

if __name__ == "__main__":
    mapping = [('/Sender', SenderRequestHandler)]
    from lib.gae import run_wsgi_app
    run_wsgi_app(mapping)
