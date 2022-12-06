function approve(nuid, advisor_id) {
    const url = "/api/advisor/approve?nuid=" + nuid + "&advisor_id=" + advisor_id;
    fetch(url).then(function (response) {
        return response.json();
    }).then(function (data) {
        console.log(data);
        alert(data.message)
        location.reload()
    }).catch(function () {
        console.log("error");
    });
}

function reject(nuid, advisor_id) {
    const url = "/api/advisor/reject?nuid=" + nuid + "&advisor_id=" + advisor_id;
    fetch(url).then(function (response) {
        return response.json();
    }).then(function (data) {
        console.log(data);
        alert(data.message)
        location.reload()
    }).catch(function () {
        console.log("error");
    });
}

function removeOneApprovedCourse(nuid, course_id, advisor_id) {
    const url = "/api/advisor/remove?nuid=" + nuid + "&course_id=" + course_id + "&advisor_id=" + advisor_id;
    fetch(url).then(function (response) {
        return response.json();
    }).then(function (data) {
        alert(data.message)
        location.reload()
    }).catch(function () {
        console.log("error");
    });

}

function addOneApprovedCourse(nuid, course_id, advisor_id) {
    const url = "/api/advisor/add?nuid=" + nuid + "&course_id=" + course_id + "&advisor_id=" + advisor_id;
    fetch(url).then(function (response) {
        return response.json();
    }).then(function (data) {
        alert(data.message)
        location.reload()
    }).catch(function () {
        console.log("error");
    });

}

function updateGPA(nuid, course_id, advisor_id, grade) {
    const url = "/api/advisor/update_gpa?nuid=" + nuid + "&course_id=" + course_id + "&advisor_id=" + advisor_id + '&grade=' +grade;
    fetch(url).then(function (response) {
        return response.json();
    }).then(function (data) {
        alert(data.message)
        location.reload()
    }).catch(function () {
        console.log("error");
    });

}


function insertNewStudent(advisor_id, nuid, name, bd, phone, campus, department, college, email, password) {
    const url = "/api/advisor/insert_student?nuid="
    + nuid +"&name=" + name + "&email=" + email + "&bdate=" + bd + "&campus=" + campus
    + "&college=" + college + "&department=" + department  + "&phone=" + phone
    + "&advisor_id=" + advisor_id + "&password=" + password;
    fetch(url).then(function (response) {
        return response.json();
    }).then(function (data) {
        alert(data.message)
        if (data.succeed == 1) {
            location.reload()
        }
    }).catch(function () {
        console.log("error");
    });

}

function updateHours(nuid, hours){
    const url = "/api/advisor/update_hours?nuid=" + nuid + "&hours=" + hours;
    fetch(url).then(function (response) {
        return response.json();
    }).then(function (data) {
        alert(data.message)
        location.reload()
    }).catch(function () {
        console.log("error");
    });
}

function updateAdvisorPhone(advisor_id, phone) {
    const url = "/api/advisor/update_phone?advisor_id=" + advisor_id + "&phone=" + phone;
    fetch(url).then(function (response) {
        return response.json();
    }).then(function (data) {
        alert(data.message)
        location.reload()
    }).catch(function () {
        console.log("error");
    });
}