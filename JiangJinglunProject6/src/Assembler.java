import java.util.*;
import java.io.*;

public class Assembler{
  
  private static final Map<String, String> compTable = new HashMap<String, String>(){{
    put("0", "0101010");
    put("1", "0111111");
    put("-1", "0111010");
    put("D", "0001100");
    put("A", "0110000");
    put("!D", "0001101");
    put("!A", "0110001");
    put("-D", "0001111");
    put("-A", "0110011");
    put("D+1", "0011111");
    put("1+D", "0011111");
    put("A+1", "0110111");
    put("1+A", "0110111");
    put("D-1", "0001110");
    put("A-1", "0110010");
    put("D+A", "0000010");
    put("A+D", "0000010");
    put("D-A", "0010011");
    put("A-D", "0000111");
    put("D&A", "0000000");
    put("A&D", "0000000");
    put("D|A", "0010101");
    put("A|D", "0010101");
    put("M", "1110000");
    put("!M", "1110001");
    put("-M", "1110011");
    put("M+1", "1110111");
    put("1+M", "1110111");
    put("M-1", "1110010");
    put("D+M", "1000010");
    put("M+D", "1000010");
    put("D-M", "1010011");
    put("M-D", "1000111");
    put("D&M", "1000000");
    put("M&D", "1000000");
    put("D|M", "1010101");
    put("M|D", "1010101");
  }};

  private static final Map<String, String> destTable = new HashMap<String, String>(){{
    put(null, "000");
    put("M", "001");
    put("D", "010");
    put("MD", "011");
    put("A", "100");
    put("AM", "101");
    put("AD", "110");
    put("AMD", "111");
  }};

  private static final Map<String, String> jumpTable = new HashMap<String, String>(){{
    put(null, "000");
    put("JGT", "001");
    put("JEQ", "010");
    put("JGE", "011");
    put("JLT", "100");
    put("JNE", "101");
    put("JLE", "110");
    put("JMP", "111");
  }};

  private static final Map<String, Integer> symbolTable = new HashMap<String, Integer>(){{
    put("SP", 0);
    put("LCL", 1);
    put("ARG", 2);
    put("THIS", 3);
    put("THAT", 4);
    put("SCREEN", 16384);
    put("KBD", 24576);
    for (int i = 0; i <= 15; i++) {
        put("R" + i, i);
    }
}};

  static int availableAddress = 16;

  public static List<String> commentRemover(List<String> lines){

    List<String> result = new ArrayList<>();
    boolean inComment = false;

    for (String line : lines){
      line = line.trim();

      if (line.isEmpty()){
        continue;
      }

      StringBuilder newLine = new StringBuilder();
      for (int i = 0; i < line.length(); i++){
        if (line.charAt(i) == '/' && i + 1 < line.length() && line.charAt(i + 1) == '*'){
          inComment = true;
        }
        else if (line.charAt(i) == '*' && i + 1 < line.length() && line.charAt(i + 1) == '/'){
          inComment = false;
          i++; // In order to skip the part of the comment.
        }
        else if (line.charAt(i) == '/' && i + 1 < line.length() && line.charAt(i + 1) == '/'){
          if (i != 0){
            newLine.append("\n");
          }
          break;
        }
        else if (!inComment){
          newLine.append(line.charAt(i));
        }
      }

      String finalLine = newLine.toString().trim().replaceAll(" ", "");
      if (!finalLine.isEmpty()){
        result.add(finalLine);
      }

    }
    return result;
  }

  public static void findLabels(List<String> lines){
    int index = 0;
    // Use the while loop to avoid modifying the list while looping through it.
    while (index < lines.size()){
      String line = lines.get(index);
      if (line.charAt(0) == '('){
        String label = line.substring(1, line.length() - 1);
        symbolTable.put(label, index);
        lines.remove(index);
      }
      else{
        index++;
      }
    }
  }

  public static String checkCompOrRegister(String line){
    if(line.charAt(0) == '@'){
      return aInstruction(line);
    }
    else{
      return cInstruction(line);
    }
  }

  public static String aInstruction(String line){
    String current = line.substring(1);
    int address;

    if (isNumeric(current)){
      address = Integer.parseInt(current);
    }
    else{
      if (!symbolTable.containsKey(current)){
        symbolTable.put(current, availableAddress);
        availableAddress++;
      }
      address = symbolTable.get(current);
    }

    String binary = Integer.toBinaryString(address);

    return String.format("%16s", binary).replace(' ', '0');
  }

  public static boolean isNumeric(String line){
    try{
      Integer.parseInt(line);
      return true;
    } catch (NumberFormatException e){
      return false;
    }
  }

  public static String cInstruction(String line){
    String comp = null, jump = null, dest = null;

    int equalIndex = line.indexOf('=');
    int semicolonIndex = line.indexOf(';');

    if (equalIndex != -1){
      dest = line.substring(0, equalIndex);
      comp = line.substring(equalIndex + 1);
      jump = null;
    }
    else if (semicolonIndex != -1){
      comp = line.substring(0, semicolonIndex);
      jump = line.substring(semicolonIndex + 1);
      dest = null;
    }

    String compBits = compTable.get(comp);
    String jumpBits = jumpTable.getOrDefault(jump, "000");
    String destBits = destTable.getOrDefault(dest, "000");

    return "111" + compBits + destBits + jumpBits;
  }

  public static void main(String[] args){
    if (args.length != 1){ // Check if the number of input arguments is correct.
      System.out.println("Please provide the correct number of input file path.");
      return;
    }

    String inputFilePath = args[0];
    String outputFilePath = inputFilePath.replaceFirst("\\.asm$", ".hack"); // Use Regular Expression to specify the path to the output file
    
    try (Scanner myReader = new Scanner(new File(inputFilePath));
      FileWriter myWriter = new FileWriter(outputFilePath)) {

      List<String> input = new ArrayList<>();
      while (myReader.hasNextLine()) {
        input.add(myReader.nextLine());
      }

      List<String> withoutComment = commentRemover(input);
      findLabels(withoutComment);

      for (String line : withoutComment) {
        if (!line.isEmpty()) {
          String newLine = checkCompOrRegister(line);
          myWriter.write(newLine + "\n");
        }
      }

      System.out.println("Successfully wrote to the file.");
    } 
    catch (FileNotFoundException e) {
      System.err.println("Input file not found: " + inputFilePath);
    } 
    catch (IOException e) {
      System.err.println("Error writing to file: " + outputFilePath);
    }
  }
}