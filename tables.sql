create table userdata(firstname varchar2(50) not null ,lastname varchar2(50),emailid varchar2(100) not null, password varchar2(50) not null, phone char(10),
	dob date,constraint unique_user unique(emailid),constraint password_check check(length(password)>=8),constraint email_check check(emailid like '%@%'));

create table room(id int primary key, floor int not null, category varchar(50) not null,price int not null, capacity int not null);
insert into room values(101,1,'NON-AC',1500,2);