package cnblogs;

public class Job{
    int jobId;
    String jobTitle;
    String tagDetail;
    String jobSummary;
    String jobRelated;
    String jobModeLink;
    String jobSeasonId;
    
    public Job(int Id, String Summary) {
        jobId = Id;
        jobSummary = Summary;
        tagDetail = "";
        jobTitle = "";
        jobRelated = "";
        jobModeLink = "";
        jobSeasonId = "";
    }
    
    public Job(int Id, String Title, String Summary) {
        jobId = Id;
        jobSummary = Summary;
        tagDetail = "";
        jobTitle = Title;
        jobRelated = "";
        jobModeLink = "";
        jobSeasonId = "";
    }
    
    public Job(int Id, String Title, String Summary, String TagDetail, String ModeLink) {
        jobId = Id;
        jobSummary = Summary;
        jobModeLink = ModeLink;
        tagDetail = TagDetail;
        jobTitle = Title;
        jobRelated = "";
        jobSeasonId = "";
    }
    
    public Job(String SeasonId, String Summary, String TagDetail) {
        jobId = 0;
        jobSummary = Summary;
        jobModeLink = "";
        tagDetail = TagDetail;
        jobTitle = "";
        jobRelated = "";
        jobSeasonId = SeasonId;
    }
    
    public int getId() {
        return jobId;
    }
    
    public String getSummary() {
        return jobSummary;
    }
    
    public String getTagDetail() {
        return tagDetail;
    }
    
    public String getTitle() {
        return jobTitle;
    }
    
    public String getJobRelated() {
        return jobRelated;
    }
    
    public String getModeLink() {
        return jobModeLink;
    }
    
    public String getSeasonId() {
        return jobSeasonId;
    }
}