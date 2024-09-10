import json
import sys
from predi.comparator  import Comparator
import re




comparator = Comparator()

def read_json(path: str):
    """Reads json and returns a dict """
    try:
        with open(path, "r") as file:
            data = json.load(file)
            return data
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None


def parse_daikon_list(predicates: list):
   """Takes a list of predicates and outputs a list of parsed predicats"""
   parsed_list = []
   for expression in predicates:
      parsed = parse_daikon(expression)
      parsed_list.append(parsed)
   return parsed_list

def parsed_to_dict(parsed:list):
   """Takes a parsed list of predicates and creates a two dicts one where the predicates are grouped according to
    their involved variabels and one where parsed predicates are mapped to their orignal format """
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
   """Takes a dict of predicates and find the strongest for each one and outputs a new list of reduced preds """
   reduced_preds = []
   for pred in preds_dict.values():
      reduced_pred = find_strongest_predicate(pred)
      reduced_preds.append(reduced_pred)

    
   return reduced_preds   


def parse_original(input: dict, list):
   """Takes input dict with orignal predicates and the the parsed and outputs a list of the orignal predicates """
   new_list = []
   for preds in list:
      for entry in preds:
         new_list.append(input[entry])
   return new_list


def reduce_json(path: str):
    """Reduces the invariants found in the path and outputs a new json"""
    f = open(path)
    data = json.load(f)
    for entry in data:
        preconditions = entry["preconditions"]
        post_conditions = entry["postconditions"]
        parsed_preconditions = parse_daikon_list(preconditions)
        parsed_postconditions = parse_daikon_list(post_conditions)
        category_preconditions_dict, parsed_preconditions_dict = parsed_to_dict(parsed_preconditions)
        category_postconditions_dict, parsed_postconditions_dict = parsed_to_dict(parsed_postconditions)
        reduced_preconditions = parse_original(parsed_preconditions_dict, find_strongest_in_dict(category_preconditions_dict))
        reduced_postconditions =parse_original(parsed_postconditions_dict, find_strongest_in_dict(category_postconditions_dict))
        # print(parse_original(parsed_preconditions_dict, reduced_preconditions))
        entry["postconditions"] = reduced_postconditions
        entry["preconditions"] =reduced_preconditions

    f = open("./output.json", "w")
    json.dump(data, f)




def find_strongest_predicate(preds: list):
    """Takes a list of predicates preds and finds the strongest ones in the list """
    for first_pred in preds:
        stronger_predicate_exists = False
        for second_pred in preds:
            result = comparator.compare(first_pred, second_pred)
            if result == 'The predicates are equivalent.':
                continue
            if result == 'The first predicate is stronger.':
                continue
            if result == 'The second predicate is stronger.':
                stronger_predicate_exists = True
        if stronger_predicate_exists:
            preds.remove(first_pred)
    return preds

      


def regex_parse(a: str):
    """Uses regex to clean daikon expression from [...], Sum(), ori() """
    a = re.sub(r'\[\.\.\.\]', 'arrayPlaceHolder', a)
    result = re.search(r'ori\(([\w\[\]\(\)\.]+)\)', a)
    if result:
        a = result.group(1)
    
    result = re.search(r'Sum\(([\w\[\]\(\)\.]+)\)', a)
    if result:
        a = result.group(1)

    return a


def split_expression(a:str):
   """Takes a predicates and splits into the a tuple of 
   (lefthandside of expression, relation, righthandside of expression)"""
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
   relation = a[1]
   return left, relation, right

def parse_daikon(a:str):
   """Takes a daikon style predicate and create a tuple of the (invovled variabels,
   orignal predicate, parsed predicate)
      
      """
   original = a
   left, delimeter, right = split_expression(a)
   left = regex_parse(left)
   right = regex_parse(right)
   return (left + " "+  right, original,  f"{left} {delimeter} {right}")


if __name__ == "__main__":

   # list =  parse_daikon_list(["ori(Sum(stakingTokenBalances[...])) >= Sum(stakingTokenBalances[...])",
   #       "ori(Sum(stakingTokenBalances[...])) > Sum(stakingTokenBalances[...])",
   #       "ori(Sum(stakingTokenBalances[...])) != Sum(stakingTokenBalances[...])",
   #       "ori(Sum(stakingTokenBalances[...])) >= stakingTokenBalances[msg.sender]",
   #       "ori(Sum(stakingTokenBalances[...])) > stakingTokenBalances[msg.sender]",
   #       "ori(Sum(stakingTokenBalances[...])) != stakingTokenBalances[msg.sender]",
   #       "ori(Sum(stakingTokenBalances[...])) >= stakingTokenSupply",
   #       "ori(Sum(stakingTokenBalances[...])) > stakingTokenSupply",
   #       "ori(Sum(stakingTokenBalances[...])) != stakingTokenSupply",
   #       "Sum(stakingTokenBalances[...]) >= ori(stakingTokenBalances[msg.sender])",
   #       "Sum(stakingTokenBalances[...]) > ori(stakingTokenBalances[msg.sender])",
   #       "Sum(stakingTokenBalances[...]) != ori(stakingTokenBalances[msg.sender])",
   #       "Sum(stakingTokenBalances[...]) >= stakingTokenBalances[msg.sender]",
   #       "Sum(stakingTokenBalances[...]) > stakingTokenBalances[msg.sender]",
   #       "Sum(stakingTokenBalances[...]) != stakingTokenBalances[msg.sender]"])

   # cat, pred = parsed_to_dict(list)
   # red = find_strongest_in_dict(cat)
   # for x in red:
   #    print(x)
   # red = parse_original(pred, red)
   # print("_________________________________________________")
   # for x in red:
   #    print(x)

   path = sys.argv[1]
   reduce_json(path)

   #  print(comparator.compare("stakingTokenBalances > stakingTokenBalances", "stakingTokenBalances != stakingTokenBalances"))
   #  print(comparator.compare("x > y" ,"x != y"))
   #  # print(comparator.compare(predicate1="exampleFunction(x) > exampleFunction(y)", predicate2="exampleFunction(x) >= exampleFunction(y)"))
   #  # print(comparator.compare("x - 1 < y", "x - 1 <= y"))
   #  # print(comparator.compare("x + 1 < y", "x + 1 <= y"))
   #  # print(comparator.compare("x <= y", "x == y"))
   #  # print(comparator.compare("x >= y", "x == y"))