from predi.comparator import Comparator
import re
import json

compartor = Comparator()

test = [
      
            "ori(activeGames) != ori(minStake)",
            "ori(activeGames) >= ori(timePaused)",
            "ori(activeGames) > ori(timePaused)",
            "ori(activeGames) != ori(timePaused)",
            "ori(activeGames) <= ori(gameIdCntr)",
            "ori(activeGames) < ori(gameIdCntr)",
            "ori(activeGames) != ori(gameIdCntr)",
            "ori(activeGames) <= ori(lastProfitTransferTimestamp)",
            "ori(activeGames) < ori(lastProfitTransferTimestamp)",
            "ori(activeGames) != ori(lastProfitTransferTimestamp)",
            "ori(activeGames) <= _value",
            "ori(activeGames) < _value",
            "ori(activeGames) != _value",
            "ori(activeGames) <= ori(Sum(userGameId[...]))",
            "ori(activeGames) < ori(Sum(userGameId[...]))",
            "ori(activeGames) != ori(Sum(userGameId[...]))",
            "ori(activeGames) <= ori(houseStake)",
            "ori(activeGames) < ori(houseStake)",
            "ori(activeGames) != ori(houseStake)",
            "ori(activeGames) >= ori(Sum(pendingReturns[...]))",
            "ori(activeGames) > ori(Sum(pendingReturns[...]))",
            "ori(activeGames) != ori(Sum(pendingReturns[...]))",
    
]


def parse_daikon_list(expressions: list):

   parsed_list = []
   for expression in expressions:
      parsed = parse_daikon(expression)
      parsed_list.append(parsed)
   return parsed_list

def parsed_to_dict(parsed:list):
   category_dict = {}
   preds_dict = {}
   for pred in parsed:
      big_key ,k, v = pred
      if big_key in category_dict:
         category_dict[big_key] = category_dict[big_key] + [v]
      else:
         category_dict[big_key] = [v]
      preds_dict[v] = k

   return category_dict, preds_dict      


def find_strongest_in_dict(preds_dict: dict):
   reduced_preds = []
   for pred in preds_dict.values():
      reduced_pred = find_strongest_predicate(pred)
      reduced_preds.append(reduced_pred)

    
   return reduced_preds   


def parse_original(input: dict, list):
   new_list = []
   for preds in list:
      for entry in preds:
         new_list.append(input[entry])
   return new_list


def parse_json(path: str):
   f = open(path)
   data = json.load(f)
   for entry in data:
      preconditions = entry["preconditions"]
      post_conditions = entry["postconditions"]
      parsed_preconditions = parse_daikon_list(preconditions)
      parsed_postconditions = parse_daikon_list(post_conditions)
      category_preconditions_dict, parsed_preconditions_dict = parsed_to_dict(parsed_preconditions)
      category_postconditions_dict, parsed_postconditions_dict = parsed_to_dict(parsed_postconditions)
      reduced_preconditions = find_strongest_in_dict(category_preconditions_dict)
      reduced_postconditions = find_strongest_in_dict(category_postconditions_dict)
      print(reduced_preconditions)
      print(parse_original(parsed_preconditions_dict, reduced_preconditions))
      print("________")



      





def regex_parse(a: str):
    a = re.sub(r'\[\.\.\.\]', 'arrayPlaceHolder', a)
    result = re.search(r'ori\(([\w\[\]\(\)\.]+)\)', a)
    if result:
        a = result.group(1)
    
    result = re.search(r'Sum\(([\w\[\]\(\)\.]+)\)', a)
    if result:
        a = result.group(1)

    return a


def split_expression(a:str):
   if ">=" in a:
      a =  re.split("(\>=)",a)
   if "<=" in a:
      a =  re.split("(\<=)",a)   
   elif "==" in a:
      a = re.split("(\==)",a)
   elif "!=" in a:
      a = re.split("(\!=)",a)   
   elif ">" in a:
      a = re.split("(\>)",a)   
   elif "<" in a:
      a = re.split("(\<)",a)

   left = a[0]
   right = a[-1]
   delimeter = a[1]
   return left, delimeter, right

def parse_daikon(a:str):
   original = a
   left, delimeter, right = split_expression(a)
   left = regex_parse(left)
   right = regex_parse(right)
   return (left + " "+  right, original,  f"{left} {delimeter} {right}")
   


def find_strongest_predicate(preds: list):
   for first_pred in preds:
      stronger_predicate_exists = False
      for second_pred in preds:

         result = compartor.compare(first_pred, second_pred)
         if result == 'The predicates are equivalent.':
            continue
         if result == 'The first predicate is stronger.':
            continue
         if result == 'The second predicate is stronger.':
            stronger_predicate_exists = True
      if stronger_predicate_exists:
         preds.remove(first_pred)
   return preds
        
         

        
       
# print(compartor.compare('activeGames != timePaused', 'activeGames >= timePaused' ))
       


category_dict= {}
preds_dict = {}




# for pred in test:
#    big_key ,k, v = parse_daikon(pred)
#    if big_key in category_dict:
#       category_dict[big_key] = category_dict[big_key] + [v]
#    else:
#       category_dict[big_key] = [v]
#    preds_dict[v] = k

# # print(preds_dict)
# print(category_dict)
   

# print(output)



# assert(Old(msg.value) == msg.value);


print(compartor.compare("msg.value", "msg.value"))

# parse_json('sok/mojtaba/0x25a5feB5aC6533fE3C4E8E8e2a55f9E1f1F8E5f0-DInterest.inv.json')





# res = compartor.compare(     "profitTransferTimeSpan <= timePaused", "profitTransferTimeSpan < timePaused")
# find_strongest_predicat(['ori(activeGames) >= ori(timePaused)', 'ori(activeGames) > ori(timePaused)', 'ori(activeGames) != ori(timePaused)'])
# print(res)