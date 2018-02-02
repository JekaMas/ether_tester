class Shh(object):
    def __init__(self, web3):
        self.web3 = web3

    def version(self):
        return self.web3.manager.request_blocking("shh_version", [])

    def info(self):
        return self.web3.manager.request_blocking("shh_info", [])

    def setMaxMessageSize(self, message_size):
        return self.web3.manager.request_blocking("shh_setMaxMessageSize", [message_size])

    def setMinPoW(self, min_pow):
        return self.web3.manager.request_blocking("shh_setMinPoW", [min_pow])

    def markTrustedPeer(self, enode):
        return self.web3.manager.request_blocking("shh_markTrustedPeer", [enode])

    def newKeyPair(self):
        return self.web3.manager.request_blocking("shh_newKeyPair", [])

    def addPrivateKey(self, private_key_hex):
        return self.web3.manager.request_blocking("shh_addPrivateKey", [private_key_hex])

    def deleteKeyPair(self, key_pair_id):
        return self.web3.manager.request_blocking("shh_deleteKeyPair", [key_pair_id])

    def hasKeyPair(self, key_pair_id):
        return self.web3.manager.request_blocking("shh_hasKeyPair", [key_pair_id])

    def shh_getPublicKey(self, key_pair_id):
        return self.web3.manager.request_blocking("shh_getPublicKey", [key_pair_id])

    def shh_getPrivateKey(self, key_pair_id):
        return self.web3.manager.request_blocking("shh_getPrivateKey", [key_pair_id])

    def newSymKey(self):
        return self.web3.manager.request_blocking("shh_newSymKey", [])

    def addSymKey(self, sym_key_hex):
        return self.web3.manager.request_blocking("shh_addSymKey", [sym_key_hex])

    def generateSymKeyFromPassword(self, password):
        return self.web3.manager.request_blocking("shh_generateSymKeyFromPassword", [password])

    def hasSymKey(self, sym_key_id):
        return self.web3.manager.request_blocking("shh_hasSymKey", [sym_key_id])

    def getSymKey(self, sym_key_id):
        return self.web3.manager.request_blocking("shh_getSymKey", [sym_key_id])

    def deleteSymKey(self, sym_key_id):
        return self.web3.manager.request_blocking("shh_deleteSymKey", [sym_key_id])

    def subscribe(self, params):
        return self.web3.manager.request_blocking("shh_subscribe", params)

    def unsubscribe(self, subscription_id):
        return self.web3.manager.request_blocking("shh_unsubscribe", [subscription_id])

    def newMessageFilter(self, params):
        return self.web3.manager.request_blocking("shh_newMessageFilter", [params])

    def deleteMessageFilter(self, filter_id):
        return self.web3.manager.request_blocking("shh_deleteMessageFilter", [filter_id])

    def getFilterMessages(self, filter_id):
        return self.web3.manager.request_blocking("shh_getFilterMessages", [filter_id])

    def post(self, params):
        return self.web3.manager.request_blocking("shh_post", [params])

