from sklearn import tree
import numpy as np
from PIL import Image
from sklearn.tree._tree import TREE_LEAF
import pickle


def visulization(vec):
    input_mtx = vec.reshape((28,28)).astype('uint16')
    im = Image.fromarray(input_mtx)
    im.show()

#load data
images=np.load('images.npy')
labels=np.load('labels.npy')

# flatten matrix
flattened_images=[]
vector_labels=[]
for i in range(len(labels)):
    flattened_images.append(np.reshape(images[i],[784]))
    vector=np.zeros(10)
    vector[labels[i]]=1
    vector_labels.append(vector)

#divide into ten class
tenclass={0:[],1:[],2:[],3:[],4:[],5:[],6:[],7:[],8:[],9:[],}
for i in range(len(labels)):
    tenclass[labels[i]].append([flattened_images[i],vector_labels[i]])

#split into three part
training_image=[]
training_label=[]
val_image=[]
val_label=[]
pre_image=[]
pre_label=[]

def add_features(mtx):
    for vec in mtx:
        avg_f = np.mean(vec)
        min_f = np.min(vec)
        max_f = np.max(vec)
        std_f = np.std(vec)
        vec = np.concatenate((vec, avg_f), axis=None)
        vec = np.concatenate((vec, min_f), axis=None)
        vec = np.concatenate((vec, max_f), axis=None)
        vec = np.concatenate((vec, std_f), axis=None)

    return mtx

for number in tenclass.keys():
    for i in range(len(tenclass[number])):
        rand=np.random.uniform()
        if rand<=0.6:
            training_image.append(tenclass[number][i][0])
            training_label.append(tenclass[number][i][1])
        # elif rand<0.75:
        #     val_image.append(tenclass[number][i][0])
        #     val_label.append(tenclass[number][i][1])
        else:
            pre_image.append(tenclass[number][i][0])
            pre_label.append(tenclass[number][i][1])

training_image=np.asarray(training_image)            
training_label=np.asarray(training_label)     
# val_image=np.asarray(val_image)     
# val_label=np.asarray(val_label)     
pre_image=np.asarray(pre_image)     
pre_label=np.asarray(pre_label)     

#if not baseline model
pre_image_f=add_features(pre_image)  
training_image_f = add_features(training_image) 


# print(np.shape(pre_image[0]))
clf = tree.DecisionTreeClassifier()

clf_depth3 = tree.DecisionTreeClassifier(max_depth=100)
clf_prune = tree.DecisionTreeClassifier(min_weight_fraction_leaf=0.005)
clf_feature = tree.DecisionTreeClassifier()
clf_Baseline = clf.fit(training_image,training_label)
clf_depth3 = clf_depth3.fit(training_image,training_label)
clf_prune = clf_prune.fit(training_image,training_label)
clf_feature = clf_feature.fit(training_image_f,training_label)



# Dump the trained decision tree classifier with Pickle
decision_tree_pkl_filename1 = 'clf_Baseline.pkl'
decision_tree_pkl_filename2 = 'clf_depth3.pkl'
decision_tree_pkl_filename3 = 'clf_prune.pkl'
decision_tree_pkl_filename4 = 'clf_feature.pkl'
# Open the file to save as pkl file
decision_tree_model_pkl1 = open(decision_tree_pkl_filename1, 'wb')
decision_tree_model_pkl2 = open(decision_tree_pkl_filename2, 'wb')
decision_tree_model_pkl3 = open(decision_tree_pkl_filename3, 'wb')
decision_tree_model_pkl4 = open(decision_tree_pkl_filename4, 'wb')

pickle.dump(clf_Baseline, decision_tree_model_pkl1)
pickle.dump(clf_depth3, decision_tree_model_pkl2)
pickle.dump(clf_prune, decision_tree_model_pkl3)
pickle.dump(clf_feature, decision_tree_model_pkl4)
# Close the pickle instances
decision_tree_model_pkl1.close()
decision_tree_model_pkl2.close()
decision_tree_model_pkl3.close()
decision_tree_model_pkl4.close()



#To Restore tuple please use below command
#clf_Baseline = pickle.load(open("clf_Baseline.pkl", 'rb'))  



#prediction and confusion matrix. Please uncomment to use different perdictions
predict=clf_Baseline.predict(pre_image)
#predict=clf_depth3.predict(pre_image)
#predict=clf_prune.predict(pre_image)
#predict=clf_feature.predict(pre_image_f)

pre_value=[]
pre_label_number=[]
confusion=np.zeros([10,10])
misclfy_3 = []
cnt = 0
for i in range(len(predict)):
    pre_value.append(np.argmax(predict[i]))
    pre_label_number.append(np.argmax(pre_label[i]))
    confusion[pre_label_number[i],pre_value[i]]+=1
    if pre_value[i]==cnt and pre_label_number[i] != pre_value[i] and len(misclfy_3)<5:
        print("label",pre_label_number[i],"perdiction value",pre_value[i])
        misclfy_3.append(pre_image[i])
        cnt+=1




print("confusion:")
print(confusion)
acc = []
for i in range(len(confusion)):
    
    acc.append(confusion[i][i]/sum(confusion[i]))
print("acc",acc,np.mean(acc))

for i in misclfy_3:
    visulization(i)
    a = input()
    if a != "":
        continue







        






