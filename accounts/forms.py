
from django import forms
from .models import Account

#ที่ต้องใช้คลาส super เพราะว่าเราต้องปรับแต่งจากสิ่งที่ได้มาจากจังโก้เพราะถ้าไม่ใช้ super class จะไม่สามารถแต่งได้


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Enter Password',
        'class':'form-control', #วิธีใส่ class ให้กล่องข้อความแต่สร้างฟังก์ชันเถอะ
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Enter Password'
    }))
     
    class Meta:
        model = Account
        fields = ['first_name','last_name','phone_number','email','password']
        

    def __init__(self,*args,**kwargs): 

        # *args คือค่าที่เป็นไม่มีชื่อคือ 1,2,3,a,b,c,[]
        # **kwargs คือค่าที่มีค่าเช่น a=1 b=2 c=3
        #เป็นการเพิ่ม อาทริบิ้วที่เป็น class ชื่อ form-control ใส่ค่าในfields
        super(RegistrationForm, self).__init__(*args,**kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter Firstname'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Lastname'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'
        for field in self.fields:   
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        clean_data = super(RegistrationForm,self).clean()
        password = clean_data.get('password')
        confirm_password = clean_data.get('confirm_password')

        #วิธีใส่คลาสให้ข้อความ error ต้องใส่ใน setting.py ไปกอปโค้ด djangomessageมาใส่
        if password != confirm_password:
            raise forms.ValidationError(
                "Password dose not matched!"
            )





