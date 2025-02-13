import { useLocation } from "react-router-dom";

const Result = () => {
  const location = useLocation();
  const result = location.state?.result; 

  return (
    <div className="flex flex-col justify-center  text-center my-10">
      <h1 className="text-3xl  pb-10">Results</h1>
      {result.prediction === '1' ? 
      (<p className="text-4xl text-green-600">The certificate is authentic</p>) :
      (<p className="text-4xl text-red-600">The certificate is fake</p>) 
    
    }
    {result.Resolved_url  && 
    <p className=" pt-5  text-3xl">Issued By:</p>
  }
    <a href={`${result.Resolved_url}`} className="text-2xl underline">{result.Resolved_url}</a>
      
      <span
      className="small text-gray-500 mt-5 italic"
      >
        **MediCheck can make mistkes.
      </span>
    </div>
  );
};

export default Result;
