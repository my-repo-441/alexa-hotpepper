# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (AbstractRequestHandler, AbstractRequestInterceptor, AbstractExceptionHandler)
import ask_sdk_core.utils as ask_utils
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_model.interfaces.audioplayer import AudioItem, Stream, PlayDirective, PlayBehavior

#地名抽出用の関数
from areas_extractor import load_areas, extract_area, map_area_to_code
#ジャンル抽出用の関数
from genres_extractor import load_genres, extract_genre, map_genre_to_code

#import pandas as pd
import re
import json
import logging
import gettext
import requests # APIを使う
import openai
import os
import boto3

#openai.api_key = os.getenv('HOTPEPPER_API_KEY')
HOTPEPPER_API_KEY = os.getenv('HOTPEPPER_API_KEY')

conversation_history = []

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        _ = handler_input.attributes_manager.request_attributes["_"]

        speak_output = "ホットペッパーだよ。"
        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        _ = handler_input.attributes_manager.request_attributes["_"]
        speak_output = "ハイ"

        return (
            handler_input.response_builder
            .speak(speak_output)
            # .ask("add a reprompt if you want to keep the session open for the user to respond")
            .response
        )

class HotPepperIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("HotPepperIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        question = slots["question"].value
        
        api_key = HOTPEPPER_API_KEY
        
        areas = load_genres("area_list.txt")
        genres = load_genres("genres_list.txt")
        
        extracted_area = extract_area(question, areas)
        extracted_genre = extract_genre(question, genres)
        
        area_code = map_area_to_code(extracted_area)
        genre_code = map_genre_to_code(extracted_genre)
        
        print(extracted_area)
        print(area_code)
        
        print(extracted_genre)
        print(genre_code)
                
        # #areaとgenreを抽出
        # area_match = re.search(r"(.+?)の", question)
        # if area_match:
        #     area = area_match.group(1) + "市"
        # else:
        #     area = "Z011"
        
        #extracted_genre = extract_genre(question, genres)

        # genre_match = re.search(r"の(.+?)を", question)
        # if genre_match:
        #     genre = genre_match.group(1)
        
        i_start = 1
        restaurant_datas=[]
        
        #while True:
        query = {
        	'key': api_key,
        	'large_area':area_code, # 東京
        	'genre':genre_code,
        	'order': 1, #名前の順
        	'start': i_start, #検索結果の何番目から出力するか
        	'count': 10, #最大取得件数
        	'format': 'json'
        }
        url_base = 'http://webservice.recruit.co.jp/hotpepper/gourmet/v1/'
        responce = requests.get(url_base, query)
        result = json.loads(responce.text)['results']['shop']
        if len(result) == 0:
        	#break
        	print("0")
        for restaurant in result:
        	restaurant_datas.append([restaurant['name'], restaurant['address'], restaurant['budget']['code'], restaurant['genre']['code']])
        i_start += 100
        print(i_start)
        print(restaurant_datas)
        
        #columns = ['name', 'address', 'budget', 'genre']
        #df_restaurants = pd.DataFrame(restaurant_datas, columns=columns)
        #print(df_restaurants)
        #df_restaurants.to_csv('restaurants_tokyo.csv')

        # SNSクライアントの作成
        sns_client = boto3.client('sns')
        
        # SNSトピックのARN
        topic_arn = 'arn:aws:sns:us-east-1:726788541449:my-test-topic'
        
        # restaurant_datasをJSON文字列に変換
        message = json.dumps({'restaurant_data': restaurant_datas}, ensure_ascii=False)
        print(message)
        
        # SNSトピックにメッセージをパブリッシュ
        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject='Restaurant Data'
        )
        
        print(response)
        speak_output = "送ったよ。"     
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("他に質問はありますか？")
                .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        _ = handler_input.attributes_manager.request_attributes["_"]
        speak_output = "どうしましたか？"

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        _ = handler_input.attributes_manager.request_attributes["_"]
        speak_output = "さようなら"

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure."
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        _ = handler_input.attributes_manager.request_attributes["_"]
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "ういいい"

        return (
            handler_input.response_builder
            .speak(speak_output)
            # .ask("add a reprompt if you want to keep the session open for the user to respond")
            .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)
        _ = handler_input.attributes_manager.request_attributes["_"]
        speak_output = "例外です。"

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


class LocalizationInterceptor(AbstractRequestInterceptor):
    """
    Add function to request attributes, that can load locale specific data
    """

    def process(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        i18n = gettext.translation(
            'data', localedir='locales', languages=[locale], fallback=True)
        handler_input.attributes_manager.request_attributes["_"] = i18n.gettext

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.



sb = SkillBuilder()

# Register intent handlers
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(HotPepperIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler())

# Register exception handlers
sb.add_exception_handler(CatchAllExceptionHandler())

# Register request and response interceptors
sb.add_global_request_interceptor(LocalizationInterceptor())



# Handler name that is used on AWS lambda
handler = sb.lambda_handler()