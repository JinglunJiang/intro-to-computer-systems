import java.io.File; // Import the File class
import java.io.FileWriter; // Import the FileWriter class
import java.io.FileNotFoundException; // Import this class to handle errors
import java.io.IOException; // Import the IOException class to handle errors
import java.util.Scanner; // Import the Scanner class to read text files

/*
A program that can take an command line argument as a path to the input file,
write the same content to an output file to the same path,
strip the leading spaces,
and strip all the comments inside the original file.
*/
public class ReadFile{
  public static void main(String args[]){
    if (args.length != 1){ // Check if the number of input arguments is correct.
      System.out.println("Please provide the correct number of input file path.");
      return;
    }

    String inputFilePath = args[0];
    String outputFilePath = inputFilePath.replaceFirst("\\.in$", ".out"); // Use Regular Expression to specify the path to the output file

    try(Scanner myReader = new Scanner(new File(inputFilePath)); FileWriter myWriter = new FileWriter(outputFilePath)){
      // Create a scanner for reading the input file, and a writer to write to the new output file
      boolean insideMultiLineComment = false; // A flag used to check if a line is currently inside a comment
      while (myReader.hasNextLine()){
        String data = myReader.nextLine();
        if (data.contains("/*")){ // Check if it is a start line of the multi-line comment
          data = data.replaceAll("/\\*.*", "");
          insideMultiLineComment = true; 
        }
        if (data.contains("*/")){ // Check if it is an end line of the multi-line comment
          data = data.replaceAll(".*\\*/", "");
          insideMultiLineComment = false;
        }
        data = data.replaceAll("//.*", "").stripLeading(); // Strip the single line comments and leading spaces
        if (data.equals("") || insideMultiLineComment){ // Skip the current line from writing if it is blank after stripping
          continue;
        }
        myWriter.write(data);
        if (myReader.hasNextLine()){ // When it is not yet the last line, change to the next line
          myWriter.write("\n");
        }
      }
      System.out.println("Successfully wrote to the file.");
    }
    catch (FileNotFoundException e){ // Catch the error when the file cannot be found
      System.out.println("No such input file.");
      e.printStackTrace();
    }
    catch (IOException e){ // Catch the IO exceptions
      System.out.println("An IO error occured.");
      e.printStackTrace();
    }
  }
}