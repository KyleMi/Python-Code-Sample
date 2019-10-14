from keras.models import Sequential
from keras.layers import Dense, Activation
import numpy as np
from PIL import Image


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

for number in tenclass.keys():
    for i in range(len(tenclass[number])):
        rand=np.random.uniform()
        if rand<=0.6:
            training_image.append(tenclass[number][i][0])
            training_label.append(tenclass[number][i][1])
        elif rand<0.75:
            val_image.append(tenclass[number][i][0])
            val_label.append(tenclass[number][i][1])
        else:
            pre_image.append(tenclass[number][i][0])
            pre_label.append(tenclass[number][i][1])

training_image=np.asarray(training_image)            
training_label=np.asarray(training_label)     
val_image=np.asarray(val_image)     
val_label=np.asarray(val_label)     
pre_image=np.asarray(pre_image)     
pre_label=np.asarray(pre_label)     




# Model Template

model = Sequential() # declare model
model.add(Dense(1000, input_shape=(28*28,), kernel_initializer='he_normal')) # first layer
model.add(Activation('relu'))
#
#
#
# Fill in Model Here
#
#Tanh
model.add(Dense(1000, kernel_initializer='he_normal'))
model.add(Activation('tanh'))
model.add(Dense(1000, kernel_initializer='he_normal'))
model.add(Activation('selu'))
#model.add(Dense(10, kernel_initializer='he_normal'))
#model.add(Activation('sigmoid'))
model.add(Dense(10, kernel_initializer='he_normal')) # last layer
model.add(Activation('softmax'))


# Compile Model
model.compile(optimizer='sgd',
              loss='categorical_crossentropy', 
              metrics=['accuracy'])

# Train Model
history = model.fit(training_image, training_label, 
                    validation_data = (val_image, val_label), 
                    epochs=20, 
                    batch_size=64)


# Report Results

print(history.history)



# prediction and confusion matrix
predict=model.predict(pre_image)
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
for i in range(len(confusion)):
    confusion[i].append(confusion[i][i]/sum(confusion[i]))
print(confusion)

for i in misclfy_3:
    visulization(i)
    a = input()
    if a != "":
        continue

#Visualization
# For each algorithm, include 3 visualizations of images that were misclassified by your best
# performing model and any observations about why you think these images were misclassified.
# You will have to create or use a visualization program that takes a 28-by-28 matrix input and
# translate it into a black-and-white image.






        






