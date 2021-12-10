import json
import random

data = """
@param {length} Int(choice[0, 45, 90, 135, 180])
@param {theta} Int(range[0, 45, 60, 1, 10])
limbs(start length theta) -> loop1(loop i 0 4)
loop1 body -> move1(move length 0)
move1 -> turn2(turn theta)
turn2 -> loop1
loop1 -> limbs(end)

@param {nval} Int(range[0, 45])
main(start nval) -> turn1(turn nval)
turn1 -> dag(limbs nval)
dag -> move8(move 5 0)
move8 -> main(end)

{"position":[40,32]} -> main(25)
"""

class Augmentor():
    def __init__(self, data):
        self.fbp = data
        self.templates = self.generate_templates()

    def extract_rule (self,rule):
        """
        extract the templating randomization rule from its definition
        """
        variable = rule[rule.find("{")+1:rule.find("}")]
        variableType = rule[rule.find("} ")+1:rule.find("(")].strip()
        ruleDef = rule[rule.find("(")+1:rule.find(")")]
        rule = {
            "variable" : variable,
            "type" : variableType,
            "rule" : ruleDef
        }
        return rule

    def generate_templates(self):
        """
        Extract variables and rules for all templates in the given FBP file
        """
        randomizers = list()
        linelist = [x for x in self.fbp.splitlines() if x]
        i = 0
        while i < len(linelist):
            print(i)
            if linelist[i][0:6] == "@param":
                rules = list()
                while linelist[i][0:6] == "@param":
                    rules.append(self.extract_rule(linelist[i]))
                    i+=1
                flowname = linelist[i][0:linelist[i].find("(")]
                startindex = i
                endtoken = flowname + "(end)"
                endindex = [j for j, line in enumerate(linelist) if endtoken in line][0]
                flow = "\n".join(linelist[startindex:endindex])
                i = i + endindex - 1
                randomizer = {
                    "name" : flowname,
                    "rules" : rules,
                    "flow" : flow
                }
                randomizers.append(randomizer)
            else :
                i+=1
        return randomizers

    def get_data(self,template):
        """
        Generate a single data sample given a template by applying randomization rules
        """
        flow = template['flow']
        for rule in template["rules"]:
            ruleType = rule["rule"][0:rule["rule"].find("[")].strip()
            ruleOptions = json.loads(rule["rule"][rule["rule"].find("["):rule["rule"].find("]")+1].strip())
            if (ruleType == "choice"):
                flow = flow.replace(rule["variable"], str(random.choice(ruleOptions)))
            elif (ruleType == "range"): 
                flow = flow.replace(rule["variable"], str(random.randint(ruleOptions[0],ruleOptions[1])))
        return flow

    def generate_data_by_flowname(self, no_of_samples, name):
        """
        Pass in number of samples and name of the flow to generate its samples
        """
        searchIndex = [ x["name"] for x in self.templates ].index(name)
        template = self.templates[searchIndex]
        for i in range(0, no_of_samples):
            flow = self.get_data(template)
            print(flow, "\n")
            return flow
            ## currently being printed, can replace with a function to output files
    
    def generate_data_bulk(self, no_of_samples):
        """
        Pass in number of samples to generate its samples for all templates
        """
        for template in self.templates:
            for i in range(0, no_of_samples):
                flow = self.get_data(template)
                print(flow, "\n") 
                return flow
                ## currently being printed, can replace with a function to output files


# augmentor = Augmentor(data)
# print(json.dumps(augmentor.templates, indent=2))

# augmentor.generate_data_by_flowname(2, "main")
# augmentor.generate_data_bulk(2)


