import os
from forms import SignUp, Login, Condition, CreateTeam, Satisfy
from flask import Flask, request, render_template, redirect, session
from models import db, UserData, ConditionData, WaitTeamData, DoneTeamData, NeedLangData, ContactData



app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    userid = session.get('userId', None)
    return render_template('home.html', userId=userid)


@app.route('/login', methods=['GET', 'POST'])
def checkValid():
    form = Login()
    if form.validate_on_submit():
        userid = form['userId'].data
        password = form['userPw'].data
        userdata = UserData.query.filter(UserData.userId == userid).first()
        if not userdata:
            form.userId.errors.append('잘못된 아이디입니다.')
            return render_template('login.html', form=form)
        elif userdata.userPw != password:
            form.userPw.errors.append("잘못된 비밀번호 입니다.")
            return render_template('login.html', form=form)
        else:
            session['userId'] = userid
            done_user = db.session.query(DoneTeamData).\
                filter(DoneTeamData.userNum == UserData.userNum).\
                filter(UserData.userId==userid).all()
            if done_user:
                return redirect('/satisfy')
            else:
                return redirect("/condition")

    return render_template('login.html', form=form)


@app.route('/satisfy', methods=['Get', 'POST'])
def ask_satisfy():
    userid = session.get('userId', None)
    form = Satisfy()
    input_sat = {'Yes':'네 다른 여행지도 보고 싶습니다.' , 'N0':'아니요 새로운 팀을 원합니다.'}
    for key in input_sat.keys():
        form.input_sat.choices.append(input_sat[key])
    if form.validate_on_submit():
        usersat = db.session.query(DoneTeamData).filter(DoneTeamData.userNum == UserData.userNum).\
            filter(UserData.userId == userid).first()
        usersat.userSat = form.data.get('input_sat')
        db.session.commit()
        if usersat.userSat == '네 다른 여행지도 보고 싶습니다.':
            return redirect('/condition')
        else:
            doneteamdata = db.session.query(DoneTeamData).filter(DoneTeamData.userSat == '아니요 새로운 팀을 원합니다.').first()
            recnum = db.session.query(WaitTeamData).filter(WaitTeamData.teamCode == doneteamdata.teamCode).first()
            recnum.teamRecNum -= 1
            db.session.delete(doneteamdata)
            db.session.commit()
            waitteamdata = db.session.query(WaitTeamData).filter(WaitTeamData.teamRecNum == 0).fisrt()
            db.session.delete(waitteamdata)
            db.session.commit()
            return redirect('/condition')
    return render_template('satisfy_x.html', form=form, userid=userid)



@app.route('/logout', methods=['GET'])
def logout():
    session.pop('userId', None)
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def insertUserData():
    form = SignUp()
    if form.validate_on_submit():
        userid = UserData.query.filter(UserData.userId == form.userId.data).first()
        if userid:
            form.userId.errors.append('이미 가입된 아이디입니다.')
        if form.userId.errors:
            return render_template('register_x.html', form=form)

        userdata = UserData()
        userdata.userId = form.data.get('userId')
        userdata.userPw = form.data.get('userPw')
        userdata.userMajor = form.data.get('userMajor')
        userdata.userLang = form.data.get('userLang')

        db.session.add(userdata)
        db.session.commit()

        return redirect('/')
    return render_template('register_x.html', form=form)

@app.route('/condition', methods=['GET', 'POST'])
def sendCondition():
    userid = session.get('userId', None)
    form = Condition()
    form.travelDes.choices = [(a.countryName) for a in NeedLangData.query.order_by(NeedLangData.countryName)]
    form.travelLang.choices = [(a.countryLang) for a in NeedLangData.query.group_by(NeedLangData.countryLang)]

    travelNum = {'2명': 2, '3명':3, '4명':4}
    for key in travelNum.keys():
        form.travelNum.choices.append(travelNum[key])

    if form.validate_on_submit():
        conditiondata = ConditionData()
        conditiondata.travelDes = form.data.get('travelDes')
        conditiondata.travelNum = form.data.get('travelNum')
        conditiondata.travelLang = form.data.get('travelLang')
        conditiondata.userNum = db.session.query(UserData.userNum).filter(UserData.userId==userid)

        db.session.add(conditiondata)
        db.session.commit()
        return redirect('/waitteam')
    return render_template('condition.html', form=form, userid=userid)


@app.route('/teamcreate', methods=['GET', 'POST'])
def insertWaitTeamData():
    userid = session.get('userId', None)
    form = CreateTeam()
    form.teamTo.choices = [(a.countryName) for a in NeedLangData.query.group_by(NeedLangData.countryName)]
    teamNumGoal = {'2명': 2, '3명': 3, '4명': 4}
    for key in teamNumGoal.keys():
        form.teamNumGoal.choices.append(teamNumGoal[key])
    if form.validate_on_submit():
        doneteamdata = DoneTeamData()
        waitteamdata = WaitTeamData()
        contactdata = ContactData()
        doneteamdata.userNum = db.session.query(UserData.userNum).filter(UserData.userId==userid)
        waitteamdata.teamName = form.data.get('teamName')
        waitteamdata.teamIntro = form.data.get('teamIntro')
        waitteamdata.teamTo = form.data.get('teamTo')
        waitteamdata.teamNumGoal = form.data.get('teamNumGoal')
        contactdata.teamAddress = form.data.get('teamAddress')
        waitteamdata.teamRecNum = 1
        doneteamdata.teamCode = db.session.query(WaitTeamData.teamCode).filter(WaitTeamData.teamName==waitteamdata.teamName)
        contactdata.teamCode = db.session.query(WaitTeamData.teamCode).filter(WaitTeamData.teamName==waitteamdata.teamName)
        db.session.add(doneteamdata)
        db.session.add(waitteamdata)
        db.session.add(contactdata)
        db.session.commit()

        return redirect('/')
    return render_template('teamcreate_x.html', form=form, userid=userid)

@app.route('/waitteam', methods=['GET', 'POST'])
def findTeam():
    userid = session.get('userId', None)
    recent_id = db.session.query(ConditionData.id).order_by(ConditionData.id.desc()).first()
    team_list = db.session.query(WaitTeamData).\
        filter(WaitTeamData.teamTo == ConditionData.travelDes, WaitTeamData.teamNumGoal == ConditionData.travelNum, WaitTeamData.teamRecNum < WaitTeamData.teamNumGoal).\
        filter(ConditionData.id == recent_id[0]).all()

    return render_template('teamlist.html', userid=userid, team_list=team_list)

@app.route('/teaminfo/<int:teamCode>', methods=['GET', 'POST'])
def teaminfo(teamCode):
    userid = session.get('userId', None)
    team = WaitTeamData.query.get_or_404(teamCode)
    userLang_list = db.session.query(UserData.userLang).\
        filter(UserData.userNum==DoneTeamData.userNum).\
        filter(DoneTeamData.teamCode == teamCode).\
        group_by(UserData.userLang).all()

    return render_template('teaminfo.html', team=team, userLang_list=userLang_list, userid=userid)

@app.route('/teaminfo/end_x/<int:teamCode>', methods=['GET', 'POST'])
def getAddress(teamCode):
    userid = session.get('userId', None)
    team = ContactData.query.get(teamCode)
    user = DoneTeamData(teamCode=teamCode, userNum=db.session.query(UserData.userNum).filter(UserData.userId==userid))
    recnum = db.session.query(WaitTeamData).filter(WaitTeamData.teamCode == teamCode).first()
    recnum.teamRecNum += 1
    db.session.add(user)
    db.session.commit()

    return render_template('end_x.html', team=team, userid=userid)




basedir = os.path.abspath(os.path.dirname(__file__))
dbfile = os.path.join(basedir, 'db.sqlite')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'jawelfusidufhxkcljvhwiul'

db.init_app(app)
db.app = app
db.create_all()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)



#합류한 팀에는 더이상 팀합류 버튼 불가
#teamRecNum == 0 인 팀은 지우기
#teamNumGoal에 도달한 팀은 팀합류 버튼 불가