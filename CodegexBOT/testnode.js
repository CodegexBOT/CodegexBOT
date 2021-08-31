const fs = require('fs');
var format = require('string-format') 
const child_process = require('child_process')
let rawdata = fs.readFileSync('pattern_dict.json');
let pattern_dict = JSON.parse(rawdata);
let file_name = 'CodegexBOT'+'_'+'test-repo'+'_'+'3'+'.json'
let args3 = './rbugs/files/report_files/'+file_name
let rawdata_report = fs.readFileSync(args3);
let report = JSON.parse(rawdata_report)
let items = report['items']
let body
let comments = []
for(let i = 0; i < items.length;i++){
    let commit_sha = items[i]['commit_sha']
    changebody(items[i]['type'])
    comments.push({
        path:items[i]['file_name'],
        body:body
    })
}
console.log(comments[0])
function changebody(pattern_name){
    let category_name = pattern_dict[pattern_name]['category_name']
    let category_href = pattern_dict[pattern_name]['category_href']
    let des_title = pattern_dict[pattern_name]['des_title']
    let des_detail = pattern_dict[pattern_name]['des_detail']
    let pattern_href = pattern_dict[pattern_name]['pattern_href']
    body = format('I detect that this code is problematic. According to the [{}]\
    ({}), [{}]({}).{}',category_name,category_href,des_title,des_detail,pattern_href)
}

// async function gogo(){
//     await getPullRequestInfo()
    

// }

// function getPullRequestInfo(){
//     return new Promise((res,rej)=>{
//         let cmd = 'python3 testscr.py'
//         child_process.exec(cmd, function (err, stdout, stderr) {
//             if (err) {
//               console.log(err);
//             } else {
//               console.log(stdout);
//             }
//           })
//     })
// }