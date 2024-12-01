from flask import Flask, request

app = Flask(__name__)
messages = {}


@app.route("/")
def api() :
    if request.args.get("receive") == "True" :
        try :
            res = {
                "message" : messages[request.args.get("name")]["message"]
            }
            del messages[request.args.get("name")]
            return res
        except KeyError :
            return {}
    elif request.args.get("receive") == "False" :
        messages[request.args.get("target")] = {
            "message" : request.args.get("message"),
            "name" : request.args.get("name")
        }
        return {}


if __name__ == "__main__" :
    app.run("127.0.0.1", 5000, debug=True)
