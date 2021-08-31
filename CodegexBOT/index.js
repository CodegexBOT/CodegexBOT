/**
 * This is the main entrypoint to your Probot app
 * @param {import('probot').Probot} app
 */
const fs = require('fs');
const child_process = require('child_process')
var format = require('string-format') 
let rawdata = fs.readFileSync('pattern_dict.json');
let pattern_dict = JSON.parse(rawdata);
let MongoClient = require('mongodb').MongoClient;
let mongoURL = "mongodb://localhost:27017/";

module.exports = (app) => {
  app.log.info("CodegexRun~");
  app.on('pull_request.opened', getPullRequestInfo);
  app.on('pull_request.synchronize', updatePullRequest);
  //app.onAny(async (context) => {
  //    context.log.info({ event: context.name, action: context.payload.action });
  //  });
}


async function getPullRequestInfo(context){
  let repo_name = context.payload.repository.name
  let number = context.payload.number
  let owner_name = context.payload.repository.full_name.split('/')[0]
  let pull_data
  console.log("hei")
  await context.octokit.rest.pulls.listFiles({
    owner: owner_name,
    repo: repo_name,
    pull_number:number,
  }).then(res =>{
     pull_data  = JSON.stringify(res.data)
  })
  let file_name = owner_name+'_'+repo_name+'_'+number+'.json'
  let args1 = owner_name+'/'+repo_name+'/'+number
  let cmd = "python ./rbugs/execution_unit.py "+args1
  await child_process.execSync(cmd,{input:pull_data})
  let report;
  let db = await MongoClient.connect(mongoURL); 
  let whereStr = {"repo":repo_name,"user":owner_name,"id":number.toString()};
  report = await db.db("local").collection("report").find(whereStr).sort({time:-1}).toArray();
  db.close()
  if(report.length > 0){
  let items = report[0]['items']
  let mybody
  let comments = []
  let comments_path = []
  let comments_body = []
  for(let i = 0; i < items.length; i++){
    let commit_sha = items[i]['commit_sha']
    changebody(items[i]['type'])
    await context.octokit.rest.pulls.createReviewComment({
      owner: owner_name,
      repo: repo_name,
      pull_number: number,
      body: mybody,
      commit_id:commit_sha,
      path: items[i]['file_name'],
      position: items[i]['line_no']
    })
    console.log("========")
  }
  if(items.length <= 0 ){
   await context.octokit.rest.issues.createComment({
      owner: owner_name,
      repo: repo_name,
      issue_number: number,
      body: "Codegex haven't found potential bug. :smiley:\n\n[View Summary](http://codegex.top:5000?repo=" + repo_name + "&user=" + owner_name + ")"
    })

  }else{
	let report_url = "http://codegex.top:5000/?repo="+repo_name+"&user="+owner_name  
	let comment_body = "Codegex has summarized all bug reports for this repository. [View Summary](" + report_url + ")";
	await context.octokit.rest.issues.createComment({
      owner: owner_name,
      repo: repo_name,
      issue_number: number,
      body: comment_body
    })

 
  }

  function changebody(pattern_name){
    let category_name = pattern_dict[pattern_name]['category_name']
    let category_href = pattern_dict[pattern_name]['category_href']
    let des_title = pattern_dict[pattern_name]['des_title']
    let des_detail = pattern_dict[pattern_name]['des_detail']
    let pattern_href = pattern_dict[pattern_name]['pattern_href']
    mybody = format('I detect that this code is problematic. According to the [{}]({}), [{}]({}).{}',category_name,category_href,des_title,des_detail,pattern_href)
}
}else{
    
}
}

async function updatePullRequest(context){
  let repo_name = context.payload.repository.name;
  let number = context.payload.number;
  let owner_name = context.payload.repository.full_name.split('/')[0];
  let pull_data
  await context.octokit.rest.pulls.listReviewComments({
    owner: owner_name,
    repo: repo_name,
    pull_number: number
  }).then(res =>{
     pull_data  = res.data
     console.log(JSON.stringify(pull_data))
  });
  for (let c in pull_data) {
    console.log("================"+pull_data[c] + "====")
    if (pull_data[c]["user"]["id"] == 82792765) {
      await context.octokit.rest.pulls.deleteReviewComment({
        owner: owner_name,
        repo: repo_name,
        comment_id: pull_data[c].id
      });
    }
  }
  getPullRequestInfo(context);
}

