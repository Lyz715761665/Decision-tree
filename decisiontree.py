import sys
import math 
import copy

def gain_data(filename):
    #read from file for data
    
    file=open(filename,"r")
    attribute=file.readline()
    num=0
    att_arr=[]
    var_arr=[]
    for i in attribute.split("\t"):
        #attribute array
        att_arr.append(i)

    variable=file.readlines()
    for j in variable:
        #variable array
        var_arr.append(j.split("\t"))

    att_arr.pop()

    
    return att_arr,var_arr
        
def B(q):
    #calculate entropy
    entropy=-(q*math.log2(q)+(1-q)*math.log2(1-q))
    return entropy

def remainder(distinct,exa_num):
    #calculate remainder
    count=0
    for key in distinct:
        if distinct[key][0]==0:
            count=count
        elif distinct[key][1]==distinct[key][0]:
            count=count
        else:
            count+=(distinct[key][1]/exa_num)*B(distinct[key][0]/distinct[key][1])
    
    return count

def class_counts(var,location):
    """Counts the number of each type of example in a dataset."""
    counts = {}  # a dictionary of label -> count.
    for row in var:
        # create dict for the attribute 
        label = row[location]
        if label not in counts:
            counts[label] = [0,0]
        if label in counts:
            if row[-1]=="yes\n":
                counts[label][0]+=1
            counts[label][1] += 1
    return counts

def info_gain(att,var,A):
    #calculate information gain
    att_num=0
    exa_num=0
    location=0
    positive_num=0

    for i in att:
        #find attribute position
        if i == A:
            location=att_num
        att_num+=1
    
    for j in var:

        exa_num+=1
        if j[-1]=="yes\n":
            #calculate positive examples
            positive_num+=1

    distinct=class_counts(var,location)
    
    q=positive_num/exa_num
    
    if 0<q<1:
        goal=B(q)
    elif q>1:
        #dataset check
        return AttributeError("Problematic dataset")
    else:
        return 0
    
    if remainder(distinct,exa_num)>0:
        #calculate information gain
        gain=goal-remainder(distinct,exa_num)
    elif remainder(distinct,exa_num)==0:
        gain=goal
    else:
        #no information gain attribute
        return 0

    return gain

def partition(att,var,A):
    #Partitions a dataset on Attribute A
    
    att_num=0
    location=0
    
    for i in att:
        if i == A:
            location=att_num
        att_num+=1

    group={}
    #find unique variable
    unique=sorted(set([row[location] for row in var]))

    for value in unique:
        group[value]=[]
        
    for row in var:
        group[row[location]].append(row)
    
    return group

def generate_root(att,var):
    #find the attribute with largest information gain
    start=float("-inf")
    steps=0
    for i in att:
        value=info_gain(att,var,i)

        if value>start:
            start=value
            root=i
            location=steps

        steps+=1
    return start,root,location

class Leaf:
    #A Leaf node classifies data. Yes/No
    
    def __init__(self, classification):
        self.classification = classification

    def get_classification(self):
        return self.classification


def build_tree(att,var,depth=1,tree=None):
    gain,root,location=generate_root(att,var)
    if tree==None:
        tree={}
        tree[root]={}

    max_depth=len(att)

    if gain == 0:
        #no information gain, all classification agree
        for i in var:
            if i[-1]=="yes\n":
                return Leaf("yes").get_classification()
            else:
                return Leaf("no").get_classification()
        
        
    
    if depth==max_depth:
        #no more recursion as all attribute used
        yes_count=0
        no_count=0
        for i in var:
            if i[-1]=="yes\n":
                yes_count+=1
            else:
                no_count+=1
        if no_count>=yes_count:
            #plurality classification
            return Leaf("no").get_classification()
        else:
            return Leaf("yes").get_classification()

    #Do partiontion use the attribute with largest information gain
    next=partition(att,var,att[location])

    
    for key in next:
        #Build tree recursively, with depth increment
        tree[root][key]=build_tree(att,next[key],depth+1,tree=None)


    
    return tree

def prediction(test_array,tree):
    #default no for unknown variable
    value="no"
    if tree=="yes":
        return "yes"
    elif tree=="no":
        return "no"

    for key in tree:
        if len(tree)==1:
            #go into dict recursively
            value=prediction(test_array,tree[key])
        else:
            if key in test_array:
                 value=prediction(test_array,tree[key])

    return value

def calcuate_node(tree):
    string=str(tree).split()
    return len(string)




if __name__ == "__main__":
    data=gain_data(sys.argv[1])
    #calculate accuray
    train_total_attempt=0
    train_wrong_attempt=0
    test_total_attempt=0
    test_wrong_attempt=0
    

    #Build tree using all
    tree=build_tree(data[0],data[1])
    print("The decision tree built from all of the training set",sys.argv[1])
    print(tree)

    #Calculate number of nodes
    node_number=calcuate_node(tree)
    print("The number of nodes is",node_number)
        


    for value in data[1]:
        train_total_attempt+=1
        result=prediction(value,tree)
        if result != value[-1].strip('\n'):
            train_wrong_attempt+=1

    train_accuracy=1-train_wrong_attempt/train_total_attempt
    print("Training set accuracy is ", train_accuracy,"\n")



#leave-one-out cross-validation

    for example in data[1]:
        test_total_attempt+=1

        #make copy to not change the complete training set
        testing_set=example.copy()
        

        #leave out testing set
        training_set=data[1].copy()
        training_set.pop(training_set.index(example))

        #build tree and make prediction
        tree=build_tree(data[0],training_set)
        result=prediction(testing_set,tree)

        #check result
        if result != example[-1].strip('\n'):
            test_wrong_attempt+=1

    #use for visualizing decision tree
    

    test_accuracy=1-test_wrong_attempt/test_total_attempt
    print("Test set accuracy using leave-one-out cross-validation is ", test_accuracy)


       

    
