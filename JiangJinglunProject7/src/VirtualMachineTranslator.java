import java.io.*;
import java.util.*;
import java.nio.file.*;

public class VirtualMachineTranslator{

  private static final String[] ARITHMETIC_COMMANDS = {"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"};

  private static final String[] MEMORY_ACCESS_COMMANDS = {"push", "pop"};

  private static final String[] SEGMENT_MAP = {"argument", "local", "this", "that"};

  private static final String[] TEMP_SEGMENTS = {"0", "1", "2", "3", "4", "5", "6", "7"};

  private static final String STATIC_SEGMENT = "static";

  private static final String POINTER_SEGMENT = "pointer";

  private static final String CONSTANT_SEGMENT = "constant";

  private static int labelCounter = 0;

  public static void main(String[] args){
    if (args.length == 0){
      System.err.println("Usage: java VirtualMachineTranslator <input-file>");
      return;
    }

    String inputFileName = args[0];
    String outputFileName = inputFileName.replace(".vm", ".asm");

    try{
      List<String> commands = Files.readAllLines(Paths.get(inputFileName));
      List<String> translatedCommands = translateVMtoASM(commands);
      writeLinesToFile(outputFileName, translatedCommands);
      System.out.println("Translation completed. Output file: " + outputFileName);
    } catch (IOException e){
      System.err.println("Error reading input file: " + e.getMessage());
    }
  }

  private static void writeLinesToFile(String fileName, List<String> lines){
    try(FileWriter writer = new FileWriter(fileName)){
      for (String line : lines){
        writer.write(line);
      }
    } catch(IOException e){
      System.err.println("Error writing to file: " + e.getMessage());
    }
  }

  private static List<String> translateVMtoASM(List<String> commands){
    List<String> translatedCommands = new ArrayList<>();
    for (String command : commands){
      String[] parts = command.split("\\s+");
      if (parts.length == 0){
        continue;
      }
      if (isArithmeticCommand(parts[0])){
        translatedCommands.add(translateArithmeticCommand(parts[0]));
      }
      else if (isMemoryAccessCommand(parts[0])){
        translatedCommands.add(translateMemoryAccessCommand(parts));
      }
    }
    return translatedCommands;
  }

  private static boolean isArithmeticCommand(String command){
    for (String cmd : ARITHMETIC_COMMANDS){
      if (cmd.equals(command)){
        return true;
      }
    }
    return false;
  }

  private static boolean isMemoryAccessCommand(String command){
    for (String cmd : MEMORY_ACCESS_COMMANDS){
      if (cmd.equals(command)){
        return true;
      }
    }
    return false;
  }

  private static String translateArithmeticCommand(String command){
    StringBuilder asmCode = new StringBuilder();
    switch(command){
      case "add":
        asmCode.append("// add\n");
        asmCode.append("@SP\n");
        asmCode.append("AM=M-1\n");
        asmCode.append("D=M\n");
        asmCode.append("A=A-1\n");
        asmCpde.append("M=D+M\n");
        break;
      case "sub":
        asmCode.append("// sub\n");
        asmCode.append("@SP\n");
        asmCode.append("AM=M-1\n");
        asmCode.append("D=M\n");
        asmCode.append("A=A-1\n");
        asmCode.append("M=M-D\n");
        break;
      case "neg":
        asmCode.append("// neg\n");
        asmCode.append("@SP\n");
        asmCode.append("A=M-1\n");
        asmCode.append("M=-M\n");
        break;
      case "eq":
        asmCode.append("// eq\n");
        asmCode.append("@SP\n");
        asmCode.append("AM=M-1");
        asmCode.append("D=M\n");
        asmCode.append("A=A-1\n");
        asmCode.append("D=M-D\n");
        asmCode.append("@EQUAL").append(labelCounter).append("\n");
        asmCode.append("D;JEQ\n");
        asmCode.append("@SP\n");
        asmCode.append("A=M-1\n");
        asmCode.append("M=0\n");
        asmCode.append("(EQUAL" + labelCounter + ")\n");
        labelCounter++;
        break;
      case "gt":
        asmCode.append("// gt\n");
        asmCode.append("@SP\n");
        asmCode.append("AM=M-1\n");
        asmCode.append("D=M\n");
        asmCode.append("A=A-1\n");
        asmCode.append("D=M-D\n");
        asmCode.append("M=-1\n");
        asmCode.append("@GREATER_THAN" + labelCounter + "\n");
        asmCode.append("D;JGT\n");
        asmCode.append("@SP\n");
        asmCode.append("A=M-1\n");
        asmCode.append("M=0\n");
        asmCode.append("GREATER_THAN" + labelCounter + "\n");
        labelCounter++;
        break;
      case "lt":
        asmCode.append("// lt\n");
        asmCode.append("@SP\n");
        asmCode.append("AM=M-1\n");
        asmCode.append("D=M\n");
        asmCode.append("A=A-1\n");
        asmCode.append("D=M-D\n");
        asmCode.append("M=-1\n");
        asmCode.append("@LESS_THAN" + labelCounter + "\n");
        asmCode.append("D;JLT\n");
        asmCode.append("@SP\n");
        asmCode.append("A=M-1\n");
        asmCode.append("M=0\n");
        asmCode.append("(LESS_THAN" + labelCounter + ")\n");
        labelCounter++;
        break;
      case "and":
        asmCode.append("// and\n");
        asmCode.append("@SP\n");
        asmCode.append("AM=M-1\n");
        asmCode.append("D=M\n");
        asmCode.append("A=A-1\n");
        asmCode.append("M=D&M\n");
        break;
      case "or":
        asmCode.append("// or\n");
        asmCode.append("@SP\n");
        asmCode.append("AM=M-1\n");
        asmCode.append("D=M\n");
        asmCode.append("A=A-1\n");
        asmCode.append("M=D|M\n");
        break;
      case "not":
        asmCode.append("// not\n");
        asmCode.append("@SP\n");
        asmCode.append("A=M-1\n");
        asmCode.append("M!=M\n");
        break;
      default:
        break;
    }
    return asmCode.toString();
  }

  private static String pushDToStack(){
    return "@SP\n" + 
            "A=M\n" +
            "M=D\n" +
            "@SP\n" +
            "M=M+1\n";
  }

  private static String getSegmentPointer(String segment){
    switch (segment){
      case "local":
        return "LCL";
      case "argument":
        return "ARG";
      case "this":
        return "THIS";
      case "that":
        return "THAT";
      default:
        return "";
    }
  }

  private static String translateMemoryAccessCommand(String[] parts){
    StringBuilder asmCode = new StringBuilder();
    String segment = parts[1];
    String index = parts[2];
    switch (parts[0]){
      case "push":
        switch(segment){
          case "constant":
            asmCode.append("// push constant ").append(index).append("\n");
            asmCode.append("@").append(index).append("\n");
            asmCode.append("D=A\n");
            asmCode.append(pushDToStack());
            break;
          case "local":
          case "argument":
          case "this":
          case "that":
            asmCode.append("// push ").append(segment).append(" ").append(index).append("\n");
            asmCode.append("@" + index + "\n");
            asmCode.append("D=A\n");
            asmCode.append("@" + getSegmentPointer(segment) + "\n");
            asmCode.append("A=D+M\n");
            asmCode.append("D=M\n");
            asmCode.append(pushDToStack());
            break;
          case "temp":
            int tempIndex = Integer.parseInt(index);
            asmCode.append("// push temp ").append(tempIndex).append("\n");
            asmCode.append("@R").append(5 + tempIndex).append("\n");
            asmCode.append("D=M\n");
            asmCode.append(pushDToStack());
            break;
          case "static":
            String staticName = parts[0] + "." + index;
            asmCode.append("// push static ").append(index).append("\n");
            asmCode.append("@" + staticName + "\n");
            asmCode.append("D=M\n");
            asmCode.append(pushDToStack());
            break;
          case "pointer":
            int pointerIndex = Integer.parseInt(index);
            asmCode.append("// push pointer ").append(pointerIndex).append("\n");
            asmCode.append("@" + (pointerIndex == 0 ? "THIS" : "THAT") + "\n");
            asmCode.append("D=M\n");
            asmCode.append(pushDToStack());
            break;
          default:
            break;
        } 
      case "pop":
        switch(segment){
          case "local":
          case "argument":
          case "this":
          case "that":
            asmCode.append("// pop ").append(segment).append(" ").append(index).append("\n");
            asmCode.append("@SP\n");
            asmCode.append("AM=M-1\n");
            asmCode.append("D=M\n");
            asmCode.append("@" + index + "\n");
            asmCode.append("D=A\n");
            asmCode.append("@" + getSegmentPointer(segment) + "\n");
            asmCode.append("D=D+M\n");
            asmCode.append("@R13\n");
            asmCode.append("M=D\n");
            asmCode.append("@SP\n");
            asmCode.append("A=M\n");
            asmCode.append("D=M\n");
            asmCode.append("@R13\n");
            asmCode.append("A=M\n");
            asmCode.append("M=D\n");
            break;
          case "temp":
            int tempIndex = Integer.parseInt(index);
            asmCode.append("// pop temp ").append(tempIndex).append("\n");
            asmCode.append("@SP\n");
            asmCode.append("AM=M-1\n");
            asmCode.append("D=M\n");
            asmCode.append("@R").append(5 + tempIndex).append("\n");
            asmCode.append("M=D\n");
            break;
          case "static":
            String staticName = parts[0] + "." + index;
            asmCode.append("// pop static ").append(index).append("\n");
            asmCode.append("@SP\n");
            asmCode.append("AM=M-1\n");
            asmCode.append("D=M\n");
            asmCode.append("@" + staticName + "\n");
            asmCode.append("M=D\n");
            break;
          case "pointer":
            int pointerIndex = Integer.parseInt(index);
            asmCode.append("// pop pointer ").append(pointerIndex).append("\n");
            asmCode.append("@SP\n");
            asmCode.append("AM=M-1\n");
            asmCode.append("D=M\n");
            asmCode.append("@" + (pointerIndex == 0 ? "THIS" : "THAT") + "\n");
            asmCode.append("M=D\n");
            break;
          default:
            break;
        }
        break;
    }
    return asmCode.toString();
  }
}