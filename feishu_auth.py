import logging

from superset.security import SupersetSecurityManager


class CustomSsoSecurityManager(SupersetSecurityManager):
    def oauth_user_info(self, provider, response=None):
        if provider == "lark":
            me = self.appbuilder.sm.oauth_remotes[provider].get("user_info").json()['data']
            logging.debug("user_data: {0}".format(me))
            return {
                "name": me["name"],
                "email": me["user_id"] + "@kinlim.bi.com",
                "id": me["user_id"],
                "username": me["en_name"],
                "first_name": me["en_name"],
                "last_name": me["name"],
            }

 