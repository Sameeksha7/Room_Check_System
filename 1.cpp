#include<bits/stdc++.h>
using namespace std;
struct faculty{
    string name;
    bool isFree[5][7];
    void func(){
        for(int i=0;i<5;i++){
            for(int j=0;j<7;j++){
                isFree[i][j]=true;
            }
        }
    }
};
struct course{
    string code;
    faculty* f;
    int hours;
};
struct batch{
    string name;
    int courses;
    vector<course*>course_list;
};

bool cmp1(batch b1,batch b2){
    return b1.name<b2.name;
}
bool cmp2(course c1,course c2){
    return c1.code<c2.code;
}
bool isPossible(course* c,string table[5][7],int i,int j){
    faculty *f=c->f;
    if(f->isFree[i][j]==false) return false;
    if(table[i][j]!="NIL") return false;
    if(c->hours==0) return false;
    return true;
}
bool complete(vector<course*>c_list){
    for(auto c:c_list){
        if(c->hours!=0){
            return false;
        }
    }    
    return true;
}
bool create(vector<course*>c_list,string table[5][7]){
    if(complete(c_list)) return true;
    for(int i=0;i<5;i++){
        for(int j=0;j<7;j++){
            for(int k=0;k<c_list.size();k++){
                if(isPossible(c_list[k],table,i,j)){
                    table[i][j]=c_list[k]->code;
                    c_list[k]->hours-=1;
                    faculty *f=c_list[k]->f;
                    f->isFree[i][j]=false;
                    if(create(c_list,table)){
                        return true;
                    }
                    table[i][j]="NIL";
                    c_list[k]->hours+=1;
                    f->isFree[i][j]=true;
                }
            }
        }
    }
    return false;
}
void timeTable(vector<batch*>b_list){
    
    sort(b_list.begin(),b_list.end(),cmp1);
    for(auto b:b_list){
        cout<<b->name<<"\n";
        string table[5][7];
        for(int i=0;i<5;i++){
            for(int j=0;j<7;j++){
                table[i][j]="NIL";
            }
        }
        vector<course*>c_list=b->course_list;
        sort(c_list.begin(),c_list.end(),cmp2);
        bool ans=create(c_list,table);
        if(ans)
            for(int i=0;i<5;i++){
                for(int j=0;j<7;j++){
                    cout<<table[i][j]<<" ";
                }
                cout<<"\n";
            }
        else cout<<"NIL\n";
    }
}
int main(){
    int t;
    cin>>t;
    while(t--){
        int batches;
        cin>>batches;
        vector<batch*>b_list;
        for(int i=0;i<batches;i++){
            string name;
            cin>>name;
            int courses;
            cin>>courses;
            batch *b=new batch;
            b->name=name;
            b->courses=courses;
            vector<course*>c_list;
            for(int j=0;j<courses;j++){
                string code;
                string fac;
                int hours;
                cin>>code>>fac>>hours;
                faculty *f=new faculty;
                f->name=fac;
                f->func();
                course *c=new course;
                c->code=code;
                c->f=f;
                c->hours=hours;
                c_list.push_back(c);
            }
            b->course_list=c_list;
            b_list.push_back(b);
        }
        timeTable(b_list);
    }
}