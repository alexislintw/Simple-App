function getStatisticsData() {
    fetch('/admin/statistics', {
        method : 'GET',
        headers: {
            'Content-Type': 'application/json',
            "Accept": "application/json",
        },
    })
    .then((response) => response.json())
    .then((statJson) => {
        document.getElementById('label_total_signup_users').textContent = statJson["total_users_sign_up"];
        document.getElementById('label_active_users_today').textContent = statJson["total_active_sessions_today"];
        document.getElementById('label_active_users_7days').textContent = statJson["average_active_session_in_7days"];
    }).catch((err) => {
        console.log(err);
    });
}

function convertTimestampToDatetime(unix_timestamp) {
    var date = new Date(unix_timestamp * 1000);
    var year = date.getFullYear();
    var month = date.getMonth()+1;
    var day = date.getDate();
    var hour = date.getHours();
    var min = date.getMinutes();
    var sec = date.getSeconds();
    var formatted_time = year + '/' + month + '/' + day + ' ' + hour + ':' + min + ':' + sec ;
    return formatted_time;
}

function getUserDatabase() {
    fetch('/admin/user-info-list', {
        method : 'GET',
        headers: {
            'Content-Type': 'application/json',
            "Accept": "application/json",
        },
    })
    .then((response) => response.json())
    .then((json) => {
        document.getElementById('label_total_signup_users').textContent = json["total_users_sign_up"];
        document.getElementById('label_active_users_today').textContent = json["total_active_sessions_today"];
        document.getElementById('label_active_users_7days').textContent = json["average_active_session_in_7days"];

        let strHtml = '<table class="pure-table">';
        strHtml += '<thead>';
        strHtml += '<tr>';
        strHtml += '<th>#</th>';
        strHtml += '<th>Timestamp of user sign up</th>';
        strHtml += '<th>Number of times logged in</th>';
        strHtml += '<th>Timestamp of the last user session</th>';
        strHtml += '</tr>';
        strHtml += '</thead>';
        strHtml += '<tbody>';
        for (let i = 0; i < json.length; i++) {
            user = json[i];
            strHtml += '<tr>';
            strHtml += '<td>'+user['id']+'</td>';
            strHtml += '<td>'+user['sign_up_at']+'<br/>('+convertTimestampToDatetime(user['sign_up_at'])+')</td>';
            strHtml += '<td>'+user['number_of_login']+'</td>';
            strHtml += '<td>'+user['last_user_session_at']+'<br/>('+convertTimestampToDatetime(user['last_user_session_at'])+')</td>';
            strHtml += '</tr>';
        }
        strHtml += '<tbody>';
        strHtml += '</table>';                   
        document.getElementById('div_user_database').innerHTML = strHtml;
    }).catch((err) => {
        console.log(err);
    });
}

function autoRefresh() {
    getUserDatabase();
    getStatisticsData();
}

